from __future__ import annotations

from datetime import datetime

from src.api.schemas import (
    AlertItem,
    ClaimEmailSample,
    ClaimSubmissionRequest,
    ClaimSubmissionResponse,
    CompanyDashboardResponse,
    CustomerClaim,
    CustomerDashboardResponse,
    FeatureCard,
    HomeResponse,
    PublicFeature,
    QueueItem,
)
from src.api.services.insurance_data import append_submitted_claim, load_claim_history


def build_home_payload() -> HomeResponse:
    dataframe = load_claim_history()

    # I calculate a small headline summary here so the homepage can feel like a real insurance product.
    metrics = {
        "claims_processed_today": int(min(len(dataframe), 128)),
        "live_review_queue": int((dataframe["overall_risk_label"] != "low").sum()),
        "auto_cleared_rate": f"{round((dataframe['manual_review_outcome'] == 'approved').mean() * 100)}%",
    }

    return HomeResponse(
        metrics=metrics,
        public_features=_build_public_features(),
        behavioural_fields=_build_behavioural_fields(),
        claim_email_samples=_build_claim_email_samples(),
        live_alerts=_build_alerts(limit=5),
    )


def build_customer_dashboard_payload() -> CustomerDashboardResponse:
    dataframe = load_claim_history().head(6)
    claims = [
        CustomerClaim(
            claim_id=row.claim_id,
            policy_type=f"{row.policy_type.title()} {row.coverage_tier.title()}",
            item_category=str(row.item_category).replace("_", " ").title(),
            amount=f"GBP {row.claim_amount_gbp:,.0f}",
            status=_map_customer_status(row.manual_review_outcome),
            submitted_at=row.claim_submission_timestamp.strftime("%d %b %Y, %H:%M"),
            risk_summary=row.overall_risk_label.title(),
            next_step=_build_next_step(row.manual_review_outcome, row.overall_risk_label),
        )
        for row in dataframe.itertuples()
    ]
    return CustomerDashboardResponse(claims=claims)


def build_company_dashboard_payload() -> CompanyDashboardResponse:
    dataframe = load_claim_history()
    queue_source = dataframe.head(8)
    metrics = {
        "high_risk_open": int((dataframe["overall_risk_label"] == "high").sum()),
        "review_needed": int((dataframe["overall_risk_label"] != "low").sum()),
        "avg_triage_time": "4m",
        "auto_approvals": f"{round((dataframe['manual_review_outcome'] == 'approved').mean() * 100)}%",
    }

    queue = [
        QueueItem(
            claim_id=row.claim_id,
            claimant=row.claimant_name
            if isinstance(row.claimant_name, str) and row.claimant_name.strip()
            else f"Policyholder {row.claimant_id[-4:]}",
            policy_type=f"{row.policy_type.title()} {row.coverage_tier.title()}",
            amount=f"GBP {row.claim_amount_gbp:,.0f}",
            nlp_risk=float(row.email_language_risk_score),
            document_risk=float(row.document_risk_score),
            behavioural_risk=float(row.behavioural_risk_score),
            combined_risk=_map_company_risk(row.overall_risk_label),
            alert_reason=_build_alert_reason(row),
        )
        for row in queue_source.itertuples()
    ]

    return CompanyDashboardResponse(metrics=metrics, queue=queue, live_alerts=_build_alerts(limit=7))


def build_live_alert_event(event_index: int) -> AlertItem:
    dataframe = load_claim_history()
    row = dataframe.iloc[event_index % len(dataframe)]
    timestamp = datetime.now().strftime("%H:%M")

    return AlertItem(
        id=f"ALT-{9000 + event_index + 1}",
        time=timestamp,
        severity=_map_company_risk(row["overall_risk_label"]),
        title=_build_alert_title(row),
        detail=_build_alert_reason(row),
    )


def create_submitted_claim(claim_request: ClaimSubmissionRequest, evidence_summary: dict | None = None) -> ClaimSubmissionResponse:
    # I persist the new claim first so every dashboard read after this sees the same saved record.
    claim_record = append_submitted_claim(claim_request, evidence_summary=evidence_summary)
    customer_claim = _build_customer_claim_from_record(claim_record)
    queue_item = _build_queue_item_from_record(claim_record)
    alert = AlertItem(
        id=f"ALT-{10000 + int(str(claim_record['claim_id']).split('-')[-1])}",
        time=_format_alert_time(claim_record["claim_submission_timestamp"]),
        severity=_map_company_risk(claim_record["overall_risk_label"]),
        title=_build_alert_title(_record_accessor(claim_record)),
        detail=_build_alert_reason(_record_accessor(claim_record)),
    )
    return ClaimSubmissionResponse(
        claim_id=claim_record["claim_id"],
        customer_claim=customer_claim,
        queue_item=queue_item,
        alert=alert,
        evidence_summary={
            "evidence_name": claim_record.get("evidence_name", ""),
            "evidence_storage_path": claim_record.get("evidence_storage_path", ""),
            "cv_signal_summary": claim_record.get("cv_signal_summary", ""),
            "document_risk_score": claim_record.get("document_risk_score", 0.0),
            "document_reasons": _build_document_reasons(_record_accessor(claim_record)),
        },
    )


def _build_public_features() -> list[PublicFeature]:
    return [
        PublicFeature(
            title="Faster Claim Intake",
            text="I guide policyholders through structured claim submission with evidence upload and instant progress feedback.",
        ),
        PublicFeature(
            title="Multimodal Fraud Screening",
            text="I combine claim language, document evidence, and behavioural history into one risk recommendation.",
        ),
        PublicFeature(
            title="Live Operations View",
            text="I give fraud teams a queue, alert feed, and cross-signal case context from one insurance dashboard.",
        ),
    ]


def _build_behavioural_fields() -> list[FeatureCard]:
    return [
        FeatureCard(
            name="Prior Claims Count",
            description="I use this to understand whether the claimant has a repeat-claiming pattern.",
        ),
        FeatureCard(
            name="Days Since Policy Start",
            description="I use this to identify claims that arrive very soon after policy activation.",
        ),
        FeatureCard(
            name="Days Since Last Claim",
            description="I use this to spot compressed claim timing across multiple submissions.",
        ),
        FeatureCard(
            name="High Value Purchase Flag",
            description="I use this to mark recent unusual purchases that raise behavioural risk.",
        ),
        FeatureCard(
            name="Spend Spike Flag",
            description="I use this to show when spending behaviour recently moved outside the norm.",
        ),
        FeatureCard(
            name="Account Location Change",
            description="I use this to flag sudden login geography changes before a claim.",
        ),
        FeatureCard(
            name="Multiple Devices in 7 Days",
            description="I use this to detect unusual account access patterns across devices.",
        ),
        FeatureCard(
            name="Bank Detail Change",
            description="I use this to highlight payout-risk changes close to the claim date.",
        ),
    ]


def _build_claim_email_samples() -> dict[str, ClaimEmailSample]:
    return {
        "genuine": ClaimEmailSample(
            subject="Claim for accidental damage to laptop",
            body=(
                "Dear Claims Team,\n\n"
                "I would like to submit a claim for accidental damage to my laptop under my gadget insurance policy. "
                "On 14 March 2025, I accidentally knocked a glass of water over my desk while working from home. "
                "The water spilled onto my laptop and the device stopped functioning shortly afterwards. "
                "I have attached the original purchase receipt and the repair assessment from a local technician.\n\n"
                "Kind regards,\nDaniel Morgan"
            ),
        ),
        "fraud": ClaimEmailSample(
            subject="Urgent claim request for stolen premium laptop",
            body=(
                "Dear Insurance,\n\n"
                "I need to make an urgent claim for my very expensive laptop which was stolen yesterday evening. "
                "It was worth around GBP 2,400 and I need the full payout quickly. I do not remember the exact time "
                "or location because everything happened very fast, but I have attached a receipt. "
                "I also need the payment sent to my updated bank account.\n\n"
                "Regards,\nDaniel"
            ),
        ),
    }


def _build_alerts(limit: int) -> list[AlertItem]:
    dataframe = load_claim_history().head(limit)
    alerts = []
    for index, row in enumerate(dataframe.itertuples(), start=1):
        alerts.append(
            AlertItem(
                id=f"ALT-{9000 + index}",
                time=row.claim_submission_timestamp.strftime("%H:%M"),
                severity=_map_company_risk(row.overall_risk_label),
                title=_build_alert_title(row),
                detail=_build_alert_reason(row),
            )
        )
    return alerts


def _build_customer_claim_from_record(record: dict) -> CustomerClaim:
    return CustomerClaim(
        claim_id=record["claim_id"],
        policy_type=f"{str(record['policy_type']).title()} {str(record['coverage_tier']).title()}",
        item_category=str(record["item_category"]).replace("_", " ").title(),
        amount=f"GBP {float(record['claim_amount_gbp']):,.0f}",
        status=_map_customer_status(record["manual_review_outcome"]),
        submitted_at=_format_submitted_at(record["claim_submission_timestamp"]),
        risk_summary=str(record["overall_risk_label"]).title(),
        next_step=_build_next_step(record["manual_review_outcome"], record["overall_risk_label"]),
        evidence_name=record.get("evidence_name", ""),
        evidence_status="Uploaded" if record.get("evidence_name") else "Pending",
    )


def _build_queue_item_from_record(record: dict) -> QueueItem:
    claimant_name = record.get("claimant_name") or f"Policyholder {str(record['claimant_id'])[-4:]}"
    return QueueItem(
        claim_id=record["claim_id"],
        claimant=claimant_name,
        policy_type=f"{str(record['policy_type']).title()} {str(record['coverage_tier']).title()}",
        amount=f"GBP {float(record['claim_amount_gbp']):,.0f}",
        nlp_risk=float(record["email_language_risk_score"]),
        document_risk=float(record["document_risk_score"]),
        behavioural_risk=float(record["behavioural_risk_score"]),
        combined_risk=_map_company_risk(record["overall_risk_label"]),
        alert_reason=_build_alert_reason(_record_accessor(record)),
    )


def _build_alert_title(row) -> str:
    if row.overall_risk_label == "high":
        return "Cross-signal fraud escalation"
    if row.overall_risk_label == "low":
        return "Claim cleared initial screening"
    return "Claim moved to review"


def _build_alert_reason(row) -> str:
    reasons = []
    if int(row.receipt_mismatch_flag) == 1:
        reasons.append("Amount mismatch was flagged between the claim details and the uploaded receipt.")
    if int(row.duplicate_receipt_flag) == 1:
        reasons.append("Duplicate receipt detected from an existing evidence match.")
    if int(getattr(row, "image_tamper_flag", 0)) == 1:
        reasons.append("Possible edited image detected from the uploaded receipt checks.")
    if int(row.bank_detail_change_last_30_days_flag) == 1:
        reasons.append("I detected a recent payout-detail change before submission.")
    if int(row.account_login_location_change_flag) == 1:
        reasons.append("I detected a sudden login-location change before the claim.")
    if int(row.late_night_submission_flag) == 1:
        reasons.append("I saw the claim arrive at an unusual submission time.")

    if not reasons:
        reasons.append("I found a consistent claim story, behaviour pattern, and document profile.")

    return " ".join(reasons[:2])


def _build_document_reasons(row) -> list[str]:
    reasons = []
    if int(getattr(row, "receipt_present_flag", 0)) == 0:
        reasons.append("No receipt or invoice was uploaded for this claim.")
    if int(getattr(row, "receipt_mismatch_flag", 0)) == 1:
        reasons.append("Amount mismatch was flagged between the claim details and the uploaded receipt.")
    if int(getattr(row, "duplicate_receipt_flag", 0)) == 1:
        reasons.append("Duplicate receipt detected because the file matches evidence already on record.")
    if int(getattr(row, "image_tamper_flag", 0)) == 1:
        reasons.append("Possible edited image detected from the uploaded receipt checks.")

    cv_signal_summary = str(getattr(row, "cv_signal_summary", "")).strip()
    if cv_signal_summary and cv_signal_summary != "I did not receive an evidence file for this claim.":
        reasons.append(cv_signal_summary)

    return reasons or ["Receipt file uploaded and passed the available document checks."]


def _format_submitted_at(timestamp_value) -> str:
    if hasattr(timestamp_value, "strftime"):
        return timestamp_value.strftime("%d %b %Y, %H:%M")
    return datetime.fromisoformat(str(timestamp_value)).strftime("%d %b %Y, %H:%M")


def _format_alert_time(timestamp_value) -> str:
    if hasattr(timestamp_value, "strftime"):
        return timestamp_value.strftime("%H:%M")
    return datetime.fromisoformat(str(timestamp_value)).strftime("%H:%M")


def _record_accessor(record: dict):
    class RecordAccessor:
        def __init__(self, inner_record: dict) -> None:
            self.__dict__.update(inner_record)

    return RecordAccessor(record)


def _map_customer_status(outcome: str) -> str:
    mapping = {
        "approved": "Approved",
        "flagged": "Under Review",
        "rejected": "Rejected",
    }
    return mapping.get(outcome, "Received")


def _build_next_step(outcome: str, risk_label: str) -> str:
    if outcome == "approved":
        return "I am preparing the payout."
    if outcome == "rejected":
        return "I have escalated this claim to the fraud investigation team."
    if risk_label == "high":
        return "I am verifying the uploaded evidence and account changes."
    return "I have queued the claim for routine checks."


def _map_company_risk(risk_label: str) -> str:
    mapping = {
        "high": "High",
        "medium": "Review",
        "low": "Low",
    }
    return mapping.get(risk_label, risk_label.title())
