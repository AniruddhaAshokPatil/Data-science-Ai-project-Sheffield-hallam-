from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.api.config import cfg
from src.train.model_paths import ANOMALY_METADATA, ANOMALY_MODEL, CV_CNN_MODEL, NLP_MODEL, NLP_VECTORIZER


def _file_status(path: Path, *, required: bool, description: str) -> dict[str, Any]:
    # I describe each artifact the same way so the readiness payload is easy
    # for dashboards, operators, and CI checks to understand consistently.
    exists = path.exists()
    status = "ready" if exists else ("not_ready" if required else "degraded")
    return {
        "name": description,
        "path": str(path),
        "required": required,
        "available": exists,
        "status": status,
    }


def _directory_status(path: Path, *, required: bool, description: str) -> dict[str, Any]:
    # I check directory writability here because analytics and output flows
    # depend on being able to create files at runtime in production.
    exists = path.exists()
    writable = os.access(path, os.W_OK) if exists else False
    available = exists and writable

    if available:
        status = "ready"
    elif required:
        status = "not_ready"
    else:
        status = "degraded"

    return {
        "name": description,
        "path": str(path),
        "required": required,
        "available": available,
        "status": status,
        "details": {
            "exists": exists,
            "writable": writable,
        },
    }


def get_readiness_report() -> dict[str, Any]:
    # I keep the readiness report structured because production systems need
    # more than a binary up/down signal when models are only partly available.
    components = {
        "transaction_api": {
            "name": "Transaction scoring API",
            "required": True,
            "available": True,
            "status": "ready",
        },
        "analytics_dataset": _file_status(
            cfg.card_csv,
            required=False,
            description="Analytics dataset",
        ),
        "outputs_directory": _directory_status(
            cfg.outputs_dir,
            required=True,
            description="Writable output directory",
        ),
        "nlp_corpus": _file_status(
            Path(cfg.sms_corpus),
            required=False,
            description="NLP SMS corpus",
        ),
        "nlp_model": _file_status(
            NLP_MODEL,
            required=False,
            description="NLP model artifact",
        ),
        "nlp_vectorizer": _file_status(
            NLP_VECTORIZER,
            required=False,
            description="NLP vectorizer artifact",
        ),
        "anomaly_model": _file_status(
            ANOMALY_MODEL,
            required=False,
            description="Anomaly model artifact",
        ),
        "anomaly_metadata": _file_status(
            ANOMALY_METADATA,
            required=False,
            description="Anomaly model metadata",
        ),
        "cv_model": _file_status(
            CV_CNN_MODEL,
            required=False,
            description="CV model artifact",
        ),
    }

    not_ready = [name for name, item in components.items() if item["status"] == "not_ready"]
    degraded = [name for name, item in components.items() if item["status"] == "degraded"]

    if not_ready:
        overall_status = "not_ready"
        ready = False
    elif degraded:
        overall_status = "degraded"
        ready = True
    else:
        overall_status = "ready"
        ready = True

    return {
        "status": overall_status,
        "ready": ready,
        "environment": cfg.app_env,
        "version": cfg.app_version,
        "components": components,
        "summary": {
            "ready_count": sum(1 for item in components.values() if item["status"] == "ready"),
            "degraded_count": len(degraded),
            "not_ready_count": len(not_ready),
        },
    }
