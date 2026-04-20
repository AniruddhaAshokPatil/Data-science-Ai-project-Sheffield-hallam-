from __future__ import annotations

import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from src.api.config import settings
from src.api.db import evidence_hash_exists, insert_evidence_file


ALLOWED_EVIDENCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


async def analyze_and_store_evidence(upload: UploadFile | None) -> dict:
    if upload is None or not upload.filename:
        return {
            "evidence_name": "",
            "evidence_media_type": "",
            "evidence_storage_path": "",
            "evidence_sha256": "",
            "cv_signal_summary": "I did not receive an evidence file for this claim.",
            "duplicate_receipt_flag": 0,
            "image_tamper_flag": 0,
            "document_risk_score": 0.28,
            "evidence_status": "Missing",
        }

    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_EVIDENCE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="I only accept JPG, PNG, BMP, or PDF evidence files.")

    file_bytes = await upload.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="I received an empty evidence file.")

    file_hash = hashlib.sha256(file_bytes).hexdigest()
    duplicate_match = evidence_hash_exists(file_hash)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{timestamp}_{file_hash[:12]}{suffix}"
    storage_path = settings.EVIDENCE_UPLOADS_DIR / stored_filename
    settings.EVIDENCE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    storage_path.write_bytes(file_bytes)

    document_risk_score = 0.08
    image_tamper_flag = 0
    summary_parts = [f"I stored the uploaded evidence as {stored_filename}."]

    if duplicate_match:
        document_risk_score += 0.26
        summary_parts.append("I found that the file hash already exists in the evidence history.")

    if suffix in IMAGE_EXTENSIONS:
        image_checks = _score_image_evidence(file_bytes)
        document_risk_score += image_checks["risk_delta"]
        image_tamper_flag = image_checks["image_tamper_flag"]
        summary_parts.append(image_checks["summary"])
    else:
        pdf_checks = _score_pdf_evidence(file_bytes)
        document_risk_score += pdf_checks["risk_delta"]
        summary_parts.append(pdf_checks["summary"])

    document_risk_score = round(min(document_risk_score, 0.95), 2)
    try:
        storage_path_value = str(storage_path.relative_to(settings.REPO_ROOT))
    except ValueError:
        storage_path_value = str(storage_path)

    _append_evidence_record(
        stored_filename=stored_filename,
        media_type=upload.content_type or "application/octet-stream",
        storage_path=storage_path,
        file_hash=file_hash,
    )

    return {
        "evidence_name": upload.filename,
        "evidence_media_type": upload.content_type or "application/octet-stream",
        "evidence_storage_path": storage_path_value,
        "evidence_sha256": file_hash,
        "cv_signal_summary": " ".join(summary_parts),
        "duplicate_receipt_flag": int(duplicate_match),
        "image_tamper_flag": int(image_tamper_flag),
        "document_risk_score": document_risk_score,
        "evidence_status": "Uploaded",
    }


def _score_image_evidence(file_bytes: bytes) -> dict:
    try:
        image = Image.open(BytesIO(file_bytes))
        width, height = image.size
        risk_delta = 0.0
        summary_parts = [f"I inspected the uploaded image at {width}x{height} pixels."]

        if min(width, height) < 300:
            risk_delta += 0.18
            summary_parts.append("I marked the image as unusually small for a receipt or claim document.")

        aspect_ratio = max(width, height) / max(min(width, height), 1)
        if aspect_ratio > 4:
            risk_delta += 0.08
            summary_parts.append("I found an extreme aspect ratio that may indicate cropping or an incomplete scan.")

        if image.mode in {"1", "P"}:
            risk_delta += 0.06
            summary_parts.append("I found a low-color image mode that can reduce document quality.")

        return {
            "risk_delta": round(risk_delta, 2),
            "image_tamper_flag": int(risk_delta >= 0.18),
            "summary": " ".join(summary_parts),
        }
    except (UnidentifiedImageError, OSError):
        return {
            "risk_delta": 0.3,
            "image_tamper_flag": 1,
            "summary": "I could not read the uploaded image cleanly, so I raised the document-risk score.",
        }


def _score_pdf_evidence(file_bytes: bytes) -> dict:
    size_kb = len(file_bytes) / 1024
    risk_delta = 0.06
    summary_parts = [f"I inspected the uploaded PDF metadata and found a file size of {size_kb:.1f} KB."]

    if size_kb < 25:
        risk_delta += 0.12
        summary_parts.append("I marked the PDF as unusually small for a full receipt or invoice document.")

    return {"risk_delta": round(risk_delta, 2), "summary": " ".join(summary_parts)}


def _append_evidence_record(*, stored_filename: str, media_type: str, storage_path: Path, file_hash: str) -> None:
    insert_evidence_file(
        stored_filename=stored_filename,
        media_type=media_type,
        storage_path=str(storage_path),
        file_hash=file_hash,
    )
