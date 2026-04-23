from __future__ import annotations

import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from src.api.config import settings
from src.api.db import evidence_hash_exists, insert_evidence_file


ALLOWED_EVIDENCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


async def analyze_and_store_evidence(upload: UploadFile | None) -> dict:
    if upload is None or not upload.filename:
        return {
            "evidence_name": "",
            "evidence_media_type": "",
            "evidence_storage_path": "",
            "evidence_sha256": "",
            "cv_signal_summary": "No evidence file was uploaded for this claim.",
            "analysis_reasons": ["No receipt or invoice was uploaded for this claim."],
            "duplicate_receipt_flag": 0,
            "image_tamper_flag": 0,
            "document_risk_score": 0.28,
            "evidence_status": "Missing",
        }

    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_EVIDENCE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Accepted evidence formats are JPG, PNG, BMP, TIFF, and PDF.")

    file_bytes = await upload.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded evidence file is empty.")

    file_hash = hashlib.sha256(file_bytes).hexdigest()
    duplicate_match = evidence_hash_exists(file_hash)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{timestamp}_{file_hash[:12]}{suffix}"
    storage_path = settings.EVIDENCE_UPLOADS_DIR / stored_filename
    settings.EVIDENCE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    storage_path.write_bytes(file_bytes)

    document_risk_score = 0.08
    image_tamper_flag = 0
    summary_parts = [f"The uploaded evidence was stored as {stored_filename}."]
    analysis_reasons = []

    if duplicate_match:
        document_risk_score += 0.26
        duplicate_reason = "Duplicate receipt detected because this file matches evidence already in the upload history."
        summary_parts.append(duplicate_reason)
        analysis_reasons.append(duplicate_reason)

    if suffix in IMAGE_EXTENSIONS:
        image_checks = _score_image_evidence(file_bytes)
        document_risk_score += image_checks["risk_delta"]
        image_tamper_flag = image_checks["image_tamper_flag"]
        summary_parts.append(image_checks["summary"])
        analysis_reasons.extend(image_checks["reasons"])
    else:
        pdf_checks = _score_pdf_evidence(file_bytes)
        document_risk_score += pdf_checks["risk_delta"]
        summary_parts.append(pdf_checks["summary"])
        analysis_reasons.extend(pdf_checks["reasons"])

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
        "analysis_reasons": analysis_reasons or ["Receipt file uploaded and passed the basic document checks."],
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
        summary_parts = [f"The uploaded image was inspected at {width}x{height} pixels."]
        reasons = []

        if min(width, height) < 300:
            risk_delta += 0.18
            small_image_reason = "Possible edited image because the uploaded receipt is unusually small for a genuine document."
            summary_parts.append(small_image_reason)
            reasons.append(small_image_reason)

        aspect_ratio = max(width, height) / max(min(width, height), 1)
        if aspect_ratio > 4:
            risk_delta += 0.08
            cropped_reason = "Possible cropped or incomplete receipt because the image has an extreme aspect ratio."
            summary_parts.append(cropped_reason)
            reasons.append(cropped_reason)

        if image.mode in {"1", "P"}:
            risk_delta += 0.06
            palette_reason = "Possible edited image because the receipt uses a low-colour image mode that often hides detail."
            summary_parts.append(palette_reason)
            reasons.append(palette_reason)

        return {
            "risk_delta": round(risk_delta, 2),
            "image_tamper_flag": int(risk_delta >= 0.18),
            "summary": " ".join(summary_parts),
            "reasons": reasons or ["Receipt image uploaded and passed the basic visual checks."],
        }
    except (UnidentifiedImageError, OSError):
        return {
            "risk_delta": 0.3,
            "image_tamper_flag": 1,
            "summary": "The uploaded image could not be read cleanly, so the document-risk score was raised.",
            "reasons": ["Possible edited image because the receipt could not be read as a normal image file."],
        }


def _score_pdf_evidence(file_bytes: bytes) -> dict:
    size_kb = len(file_bytes) / 1024
    risk_delta = 0.06
    summary_parts = [f"The uploaded PDF metadata was inspected and has a file size of {size_kb:.1f} KB."]
    reasons = []

    if size_kb < 25:
        risk_delta += 0.12
        pdf_reason = "Possible incomplete receipt because the PDF is unusually small for a full invoice or receipt."
        summary_parts.append(pdf_reason)
        reasons.append(pdf_reason)

    return {
        "risk_delta": round(risk_delta, 2),
        "summary": " ".join(summary_parts),
        "reasons": reasons or ["Receipt PDF uploaded and passed the basic file checks."],
    }


def _append_evidence_record(*, stored_filename: str, media_type: str, storage_path: Path, file_hash: str) -> None:
    insert_evidence_file(
        stored_filename=stored_filename,
        media_type=media_type,
        storage_path=str(storage_path),
        file_hash=file_hash,
    )
