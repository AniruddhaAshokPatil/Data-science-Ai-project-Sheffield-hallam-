from __future__ import annotations

from functools import lru_cache
import re
from threading import Lock

import pandas as pd

from src.api.config import settings
from src.api.db import fetch_submitted_claims_dataframe, insert_submitted_claim
from src.api.schemas import ClaimSubmissionRequest


SUBMITTED_CLAIMS_LOCK = Lock()
SUBMITTED_CLAIMS_COLUMNS = [
    "claim_id",
    "claimant_id",
    "claimant_name",
    "claimant_email",
    "policy_type",
    "coverage_tier",
    "policy_start_date",
    "claim_date",
    "claim_submission_timestamp",
    "claim_channel",
    "claimant_age_band",
    "claimant_tenure_days",
    "postal_region",
    "item_category",
    "item_purchase_date",
    "claimed_incident_date",
    "incident_type",
    "claim_amount_gbp",
    "estimated_item_value_gbp",
    "claim_amount_vs_item_value_ratio",
    "prior_claims_count",
    "claims_last_12_months",
    "approved_claims_last_24_months",
    "denied_claims_last_24_months",
    "days_since_last_claim",
    "days_since_policy_start",
    "premium_payment_missed_last_12_months",
    "recent_high_value_purchase_flag",
    "unusual_spend_spike_flag",
    "account_login_location_change_flag",
    "multiple_devices_last_7_days_flag",
    "address_change_last_30_days_flag",
    "phone_change_last_30_days_flag",
    "bank_detail_change_last_30_days_flag",
    "late_night_submission_flag",
    "weekend_submission_flag",
    "receipt_present_flag",
    "receipt_mismatch_flag",
    "duplicate_receipt_flag",
    "image_tamper_flag",
    "evidence_name",
    "evidence_media_type",
    "evidence_storage_path",
    "evidence_sha256",
    "cv_signal_summary",
    "email_language_risk_score",
    "behavioural_risk_score",
    "document_risk_score",
    "overall_risk_label",
    "manual_review_outcome",
]


@lru_cache(maxsize=1)
def load_claim_history() -> pd.DataFrame:
    # I merge the static insurance sample with newly submitted claims so the dashboards stay current.
    base_dataframe = pd.read_csv(settings.CLAIMS_DATA_PATH)
    submitted_dataframe = fetch_submitted_claims_dataframe()
    dataframe = pd.concat([base_dataframe, submitted_dataframe], ignore_index=True, sort=False)
    dataframe = _prepare_claim_history(dataframe)
    return dataframe


def append_submitted_claim(claim_request: ClaimSubmissionRequest, evidence_summary: dict | None = None) -> dict:
    with SUBMITTED_CLAIMS_LOCK:
        current_dataframe = load_claim_history()
        next_claim_id = _build_next_claim_id(current_dataframe)
        claim_record = _build_claim_record(claim_request, next_claim_id, evidence_summary or {})

        insert_submitted_claim(claim_record)

        # I clear the cache after every write so later API reads include the new claim.
        load_claim_history.cache_clear()
        return claim_record


def _prepare_claim_history(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()
    dataframe["claim_submission_timestamp"] = pd.to_datetime(
        dataframe["claim_submission_timestamp"],
        errors="coerce",
    )
    dataframe["claim_date"] = pd.to_datetime(dataframe["claim_date"], errors="coerce")
    for missing_column in [
        "claimant_name",
        "claimant_email",
        "evidence_name",
        "evidence_media_type",
        "evidence_storage_path",
        "evidence_sha256",
        "cv_signal_summary",
    ]:
        if missing_column not in dataframe.columns:
            dataframe[missing_column] = ""
    dataframe = dataframe.sort_values("claim_submission_timestamp", ascending=False).reset_index(drop=True)
    return dataframe


def _build_next_claim_id(dataframe: pd.DataFrame) -> str:
    numeric_ids = dataframe["claim_id"].astype(str).str.extract(r"(\d+)")[0].dropna().astype(int)
    next_number = int(numeric_ids.max()) + 1 if not numeric_ids.empty else 3000
    return f"CLM-{next_number}"


def _build_claim_record(claim_request: ClaimSubmissionRequest, claim_id: str, evidence_summary: dict) -> dict:
    from datetime import datetime, timedelta

    now = datetime.now().replace(microsecond=0)
    policy_start_date = (now - timedelta(days=claim_request.days_since_policy_start)).date().isoformat()
    claim_amount_ratio = round(
        claim_request.claim_amount_gbp / max(claim_request.estimated_item_value_gbp, 1),
        2,
    )

    duplicate_receipt_flag = max(
        int(claim_request.duplicate_receipt_flag),
        int(evidence_summary.get("duplicate_receipt_flag", 0)),
    )
    image_tamper_flag = max(
        int(claim_request.image_tamper_flag),
        int(evidence_summary.get("image_tamper_flag", 0)),
    )
    receipt_present_flag = max(
        int(claim_request.receipt_present_flag),
        1 if evidence_summary.get("evidence_name") else 0,
    )

    email_risk = _score_email_risk(claim_request.claim_story)
    behavioural_risk = _score_behaviour_risk(claim_request, claim_amount_ratio)
    document_risk = _score_document_risk(
        claim_request=claim_request,
        evidence_risk_score=float(evidence_summary.get("document_risk_score", 0.08 if receipt_present_flag else 0.28)),
        duplicate_receipt_flag=duplicate_receipt_flag,
        image_tamper_flag=image_tamper_flag,
        receipt_present_flag=receipt_present_flag,
    )
    total_risk = round((email_risk * 0.35) + (behavioural_risk * 0.4) + (document_risk * 0.25), 2)

    if total_risk >= 0.7:
        overall_risk_label = "high"
        manual_review_outcome = "flagged"
    elif total_risk >= 0.4:
        overall_risk_label = "medium"
        manual_review_outcome = "flagged"
    else:
        overall_risk_label = "low"
        manual_review_outcome = "approved"

    claimant_suffix = "".join([character for character in claim_request.claimant_name.upper() if character.isalnum()])[-4:] or "0001"
    claimant_id = f"CUST-{claimant_suffix}"

    return {
        "claim_id": claim_id,
        "claimant_id": claimant_id,
        "claimant_name": claim_request.claimant_name,
        "claimant_email": claim_request.claimant_email,
        "policy_type": claim_request.policy_type.lower(),
        "coverage_tier": claim_request.coverage_tier.lower(),
        "policy_start_date": policy_start_date,
        "claim_date": now.date().isoformat(),
        "claim_submission_timestamp": now.isoformat(),
        "claim_channel": "portal",
        "claimant_age_band": "25-34",
        "claimant_tenure_days": claim_request.days_since_policy_start,
        "postal_region": "Sheffield",
        "item_category": claim_request.item_category.lower().replace(" ", "_"),
        "item_purchase_date": now.date().isoformat(),
        "claimed_incident_date": now.date().isoformat(),
        "incident_type": claim_request.incident_type.lower().replace(" ", "_"),
        "claim_amount_gbp": round(claim_request.claim_amount_gbp, 2),
        "estimated_item_value_gbp": round(claim_request.estimated_item_value_gbp, 2),
        "claim_amount_vs_item_value_ratio": claim_amount_ratio,
        "prior_claims_count": claim_request.prior_claims_count,
        "claims_last_12_months": claim_request.claims_last_12_months,
        "approved_claims_last_24_months": max(claim_request.prior_claims_count - 1, 0),
        "denied_claims_last_24_months": 1 if claim_request.prior_claims_count >= 3 else 0,
        "days_since_last_claim": 45 if claim_request.prior_claims_count > 0 else 999,
        "days_since_policy_start": claim_request.days_since_policy_start,
        "premium_payment_missed_last_12_months": 0,
        "recent_high_value_purchase_flag": int(claim_request.recent_high_value_purchase_flag),
        "unusual_spend_spike_flag": int(claim_request.unusual_spend_spike_flag),
        "account_login_location_change_flag": int(claim_request.account_login_location_change_flag),
        "multiple_devices_last_7_days_flag": int(claim_request.multiple_devices_last_7_days_flag),
        "address_change_last_30_days_flag": int(claim_request.address_change_last_30_days_flag),
        "phone_change_last_30_days_flag": int(claim_request.phone_change_last_30_days_flag),
        "bank_detail_change_last_30_days_flag": int(claim_request.bank_detail_change_last_30_days_flag),
        "late_night_submission_flag": int(claim_request.late_night_submission_flag),
        "weekend_submission_flag": int(claim_request.weekend_submission_flag),
        "receipt_present_flag": receipt_present_flag,
        "receipt_mismatch_flag": int(claim_request.receipt_mismatch_flag),
        "duplicate_receipt_flag": duplicate_receipt_flag,
        "image_tamper_flag": image_tamper_flag,
        "evidence_name": evidence_summary.get("evidence_name", ""),
        "evidence_media_type": evidence_summary.get("evidence_media_type", ""),
        "evidence_storage_path": evidence_summary.get("evidence_storage_path", ""),
        "evidence_sha256": evidence_summary.get("evidence_sha256", ""),
        "cv_signal_summary": evidence_summary.get("cv_signal_summary", ""),
        "email_language_risk_score": email_risk,
        "behavioural_risk_score": behavioural_risk,
        "document_risk_score": document_risk,
        "overall_risk_label": overall_risk_label,
        "manual_review_outcome": manual_review_outcome,
    }


def _score_email_risk(claim_story: str) -> float:
    lowered_story = claim_story.lower()
    word_count = len(lowered_story.split())
    risk = 0.18

    suspicious_phrase_weights = {
        "urgent": 0.2,
        "as soon as possible": 0.2,
        "full payout": 0.22,
        "do not remember": 0.2,
        "don't remember": 0.2,
        "cannot remember": 0.2,
        "yesterday": 0.1,
        "updated bank account": 0.22,
        "new bank account": 0.22,
        "send the payment": 0.16,
        "very expensive": 0.12,
        "need the money": 0.2,
        "need this paid": 0.18,
        "happened very fast": 0.12,
        "not sure": 0.14,
        "i think": 0.08,
    }
    for phrase, weight in suspicious_phrase_weights.items():
        if phrase in lowered_story:
            risk += weight

    trustworthy_phrase_weights = {
        "attached the original purchase receipt": 0.16,
        "repair assessment": 0.12,
        "serial number": 0.1,
        "police report": 0.14,
        "crime reference": 0.14,
        "technician": 0.08,
        "working from home": 0.04,
        "receipt": 0.04,
        "invoice": 0.04,
        "merchant": 0.05,
    }
    for phrase, weight in trustworthy_phrase_weights.items():
        if phrase in lowered_story:
            risk -= weight

    if re.search(r"\b\d{1,2}\s+[a-z]+\s+\d{4}\b", lowered_story):
        risk -= 0.14
    if re.search(r"\b[a-z]+day evening\b|\b[a-z]+day morning\b|\b[a-z]+day afternoon\b", lowered_story):
        risk -= 0.05
    if re.search(r"gbp\s?\d[\d,]*", lowered_story):
        risk -= 0.06
    if re.search(r"\b\d{1,2}:\d{2}\b", lowered_story):
        risk -= 0.04

    if word_count < 20:
        risk += 0.22
    elif word_count < 40:
        risk += 0.1
    elif word_count >= 90:
        risk -= 0.06

    detail_markers = [
        "because",
        "when",
        "while",
        "after",
        "attached",
        "assessment",
        "reference",
        "receipt",
        "invoice",
        "repair",
    ]
    detail_hits = sum(1 for marker in detail_markers if marker in lowered_story)
    if detail_hits >= 4:
        risk -= 0.08

    return round(min(max(risk, 0.02), 0.98), 2)


def _score_behaviour_risk(claim_request: ClaimSubmissionRequest, claim_amount_ratio: float) -> float:
    risk = 0.1
    risk += min(claim_request.prior_claims_count * 0.08, 0.24)
    risk += min(claim_request.claims_last_12_months * 0.07, 0.21)
    if claim_request.days_since_policy_start <= 30:
        risk += 0.18
    if claim_amount_ratio >= 1.3:
        risk += 0.14
    for flag in [
        claim_request.recent_high_value_purchase_flag,
        claim_request.unusual_spend_spike_flag,
        claim_request.account_login_location_change_flag,
        claim_request.multiple_devices_last_7_days_flag,
        claim_request.address_change_last_30_days_flag,
        claim_request.phone_change_last_30_days_flag,
        claim_request.bank_detail_change_last_30_days_flag,
        claim_request.late_night_submission_flag,
        claim_request.weekend_submission_flag,
    ]:
        if flag:
            risk += 0.06
    return round(min(risk, 0.96), 2)


def _score_document_risk(
    *,
    claim_request: ClaimSubmissionRequest,
    evidence_risk_score: float,
    duplicate_receipt_flag: int,
    image_tamper_flag: int,
    receipt_present_flag: int,
) -> float:
    risk = evidence_risk_score if receipt_present_flag else 0.28
    if claim_request.receipt_mismatch_flag:
        risk += 0.28
    if duplicate_receipt_flag:
        risk += 0.24
    if image_tamper_flag:
        risk += 0.26
    return round(min(risk, 0.95), 2)
