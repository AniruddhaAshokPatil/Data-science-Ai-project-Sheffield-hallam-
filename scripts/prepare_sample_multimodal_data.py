import csv
import hashlib
import shutil
import sys
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.rebuild_claim_email_dataset import build_rows

SAMPLE_ROOT = PROJECT_ROOT / "data" / "sample"
CLAIMS_DIR = SAMPLE_ROOT / "claims"
EVIDENCE_DIR = SAMPLE_ROOT / "evidence"
MANIFEST_DIR = SAMPLE_ROOT / "manifests"

CLAIM_HISTORY_COLUMNS = [
    "claim_id",
    "claimant_id",
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
    "email_language_risk_score",
    "behavioural_risk_score",
    "document_risk_score",
    "overall_risk_label",
    "manual_review_outcome",
    "insurer_id",
    "policy_number",
    "claim_status",
    "customer_segment",
    "payment_method",
    "reported_loss_location",
    "police_report_flag",
    "known_fraud_history_flag",
    "claim_description_length",
    "settlement_amount_gbp",
    "payout_method",
    "device_fingerprint_change_flag",
    "ip_risk_score",
    "geo_distance_km_from_home",
    "merchant_category",
    "imei_or_serial_present_flag",
    "evidence_count",
    "adjuster_id",
    "review_queue",
    "sla_breach_flag",
    "referral_source",
    "excess_amount_gbp",
    "recovery_amount_gbp",
]

SAMPLE_SCENARIOS = [
    ("normal_receipt", "low", "approved", "receipt_valid"),
    ("urgent_genuine", "low", "approved", "receipt_valid"),
    ("missing_receipt", "medium", "flagged", "repair_quote"),
    ("duplicate_receipt", "medium", "flagged", "receipt_duplicate"),
    ("cropped_receipt", "medium", "flagged", "receipt_cropped"),
    ("tampered_receipt", "high", "flagged", "receipt_suspicious"),
    ("id_check", "medium", "flagged", "synthetic_id"),
    ("subtle_spam", "medium", "flagged", "receipt_valid"),
    ("bank_change_spam", "high", "flagged", "receipt_suspicious"),
    ("no_evidence_high", "high", "flagged", ""),
    ("repair_network", "low", "approved", "repair_quote"),
    ("mixed_evidence", "medium", "flagged", "receipt_valid"),
]


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def draw_document(path, title, lines, size=(720, 960), warning=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    accent = (168, 42, 42) if warning else (32, 80, 126)

    draw.rectangle((28, 28, size[0] - 28, size[1] - 28), outline=accent, width=4)
    draw.text((52, 54), title, fill=accent, font=font)
    y_position = 110
    for line in lines:
        draw.text((52, y_position), line, fill=(24, 24, 24), font=font)
        y_position += 38
    image.save(path)


def draw_pdf(path, title, lines):
    image_path = path.with_suffix(".png")
    draw_document(image_path, title, lines, size=(720, 960))
    Image.open(image_path).save(path, "PDF", resolution=100.0)
    image_path.unlink()


def file_sha256(path):
    if not path:
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_evidence_files():
    receipt_dir = EVIDENCE_DIR / "receipts"
    quote_dir = EVIDENCE_DIR / "repair_quotes"
    id_dir = EVIDENCE_DIR / "ids"

    files = {
        "receipt_valid": receipt_dir / "receipt_valid_001.png",
        "receipt_duplicate": receipt_dir / "receipt_duplicate_001.png",
        "receipt_cropped": receipt_dir / "receipt_cropped_001.png",
        "receipt_suspicious": receipt_dir / "receipt_suspicious_001.png",
        "repair_quote": quote_dir / "repair_quote_valid_001.pdf",
        "synthetic_id": id_dir / "synthetic_id_sample_001.png",
    }

    draw_document(
        files["receipt_valid"],
        "ShieldWise Sample Receipt",
        [
            "Retailer: Currys",
            "Item: Apple iPhone 15 Pro",
            "Serial/IMEI: APPL2025010137",
            "Total: GBP 949.00",
            "Payment: Card ending 2214",
            "Status: clear genuine sample receipt",
        ],
    )
    shutil.copyfile(files["receipt_valid"], files["receipt_duplicate"])
    draw_document(
        files["receipt_cropped"],
        "Cropped Receipt",
        ["Retailer: Apple Store", "Item: iPad Pro", "Total: GBP 899.00"],
        size=(780, 160),
        warning=True,
    )
    draw_document(
        files["receipt_suspicious"],
        "Receipt Review Required",
        [
            "Retailer: unknown online seller",
            "Item: gaming laptop",
            "Total: GBP 2299.00",
            "Serial number: missing",
            "Warning: low detail and inconsistent layout",
        ],
        size=(260, 220),
        warning=True,
    )
    draw_pdf(
        files["repair_quote"],
        "Repair Quote",
        [
            "Repair partner: Authorised Service Centre",
            "Diagnosis: cracked OLED display",
            "Parts: display assembly and seal kit",
            "Quote: GBP 372.00",
            "Evidence status: valid repair quote sample",
        ],
    )
    draw_document(
        files["synthetic_id"],
        "Synthetic ID Evidence Sample",
        [
            "Name: Aisha Khan",
            "Document type: synthetic demo ID",
            "Purpose: identity check workflow only",
            "No real personal document data is included",
        ],
        size=(640, 420),
    )

    return files


def claim_history_row(email_row, index, scenario_name, risk_label, review_outcome, evidence_key, evidence_path):
    high_risk = risk_label == "high"
    medium_risk = risk_label == "medium"
    receipt_present = int(bool(evidence_path and "receipt" in evidence_key))
    duplicate_receipt = int(evidence_key == "receipt_duplicate")
    image_tamper = int(evidence_key in {"receipt_cropped", "receipt_suspicious"})
    receipt_mismatch = int(evidence_key == "receipt_suspicious" or scenario_name == "mixed_evidence")
    email_risk = {"low": 0.08, "medium": 0.46, "high": 0.82}[risk_label]
    behaviour_risk = {"low": 0.18, "medium": 0.48, "high": 0.78}[risk_label]
    document_risk = 0.1
    if not evidence_path:
        document_risk = 0.38
    elif duplicate_receipt:
        document_risk = 0.44
    elif image_tamper:
        document_risk = 0.58
    elif "quote" in evidence_key:
        document_risk = 0.18

    return {
        "claim_id": email_row["claim_id"],
        "claimant_id": f"CUS-{index + 1:04d}",
        "policy_type": email_row["policy_type"],
        "coverage_tier": email_row["coverage_tier"],
        "policy_start_date": "2024-09-01",
        "claim_date": "2025-02-15",
        "claim_submission_timestamp": f"2025-02-{15 + index:02d}T10:{index + 10:02d}:00",
        "claim_channel": "portal",
        "claimant_age_band": ["18-24", "25-34", "35-44", "45-54"][index % 4],
        "claimant_tenure_days": 40 + (index * 37),
        "postal_region": "Sheffield",
        "item_category": email_row["device_category"],
        "item_purchase_date": "2024-11-20",
        "claimed_incident_date": "2025-02-14",
        "incident_type": email_row["incident_type"],
        "claim_amount_gbp": email_row["claim_amount_gbp"],
        "estimated_item_value_gbp": email_row["device_value_gbp"],
        "claim_amount_vs_item_value_ratio": round(float(email_row["claim_amount_gbp"]) / float(email_row["device_value_gbp"]), 2),
        "prior_claims_count": email_row["prior_claims"],
        "claims_last_12_months": email_row["claims_last_12_months"],
        "approved_claims_last_24_months": 1 if medium_risk else 0,
        "denied_claims_last_24_months": 1 if high_risk else 0,
        "days_since_last_claim": 18 if high_risk else (75 if medium_risk else 999),
        "days_since_policy_start": email_row["days_since_policy_start"],
        "premium_payment_missed_last_12_months": int(high_risk),
        "recent_high_value_purchase_flag": email_row["recent_high_value_purchase_flag"],
        "unusual_spend_spike_flag": email_row["unusual_spend_spike_flag"],
        "account_login_location_change_flag": email_row["login_location_changed_flag"],
        "multiple_devices_last_7_days_flag": email_row["multiple_devices_7_days_flag"],
        "address_change_last_30_days_flag": email_row["address_changed_recently_flag"],
        "phone_change_last_30_days_flag": email_row["phone_changed_recently_flag"],
        "bank_detail_change_last_30_days_flag": email_row["bank_details_changed_recently_flag"],
        "late_night_submission_flag": email_row["late_night_submission_flag"],
        "weekend_submission_flag": email_row["weekend_submission_flag"],
        "receipt_present_flag": email_row["receipt_present_flag"],
        "receipt_mismatch_flag": email_row["receipt_mismatch_flag"],
        "duplicate_receipt_flag": email_row["duplicate_receipt_flag"],
        "image_tamper_flag": email_row["image_tamper_suspected_flag"],
        "email_language_risk_score": email_risk,
        "behavioural_risk_score": behaviour_risk,
        "document_risk_score": document_risk,
        "overall_risk_label": risk_label,
        "manual_review_outcome": review_outcome,
        "insurer_id": "ShieldWise",
        "policy_number": f"POL-GAD-2025-{index + 42000}",
        "claim_status": "under_review" if review_outcome == "flagged" else "approved",
        "customer_segment": "demo",
        "payment_method": "direct_debit",
        "reported_loss_location": "Sheffield",
        "police_report_flag": int(email_row["incident_type"] == "theft"),
        "known_fraud_history_flag": int(high_risk),
        "claim_description_length": len(email_row["message_body"]),
        "settlement_amount_gbp": 0 if review_outcome == "flagged" else round(float(email_row["claim_amount_gbp"]) * 0.82, 2),
        "payout_method": "bank_transfer",
        "device_fingerprint_change_flag": int(high_risk),
        "ip_risk_score": 74 if high_risk else (42 if medium_risk else 12),
        "geo_distance_km_from_home": 88.0 if high_risk else (22.4 if medium_risk else 4.2),
        "merchant_category": "electronics",
        "imei_or_serial_present_flag": 0,
        "evidence_count": int(bool(evidence_path)),
        "adjuster_id": f"ADJ-{120 + index}",
        "review_queue": "fraud_queue" if high_risk else ("analyst_queue" if medium_risk else "auto_clear"),
        "sla_breach_flag": int(high_risk),
        "referral_source": "self_service",
        "excess_amount_gbp": 50,
        "recovery_amount_gbp": 0,
    }


def main():
    emails = build_rows()
    selected_emails = emails[:8] + emails[124:128]
    evidence_files = create_evidence_files()

    email_rows = []
    claim_rows = []
    evidence_rows = []
    multimodal_rows = []

    for index, (scenario_name, risk_label, review_outcome, evidence_key) in enumerate(SAMPLE_SCENARIOS):
        email_row = dict(selected_emails[index])
        evidence_path = evidence_files.get(evidence_key)
        relative_evidence_path = str(evidence_path.relative_to(PROJECT_ROOT)) if evidence_path else ""
        sha256 = file_sha256(evidence_path) if evidence_path else ""

        email_rows.append(email_row)
        claim_rows.append(
            claim_history_row(
                email_row,
                index,
                scenario_name,
                risk_label,
                review_outcome,
                evidence_key,
                evidence_path,
            )
        )
        evidence_rows.append(
            {
                "claim_id": email_row["claim_id"],
                "email_id": email_row["email_id"],
                "scenario_name": scenario_name,
                "evidence_type": evidence_key,
                "evidence_path": relative_evidence_path,
                "sha256": sha256,
                "is_duplicate_sample": int(evidence_key == "receipt_duplicate"),
                "document_label": "missing" if not evidence_key else ("suspicious" if risk_label in {"medium", "high"} else "valid"),
            }
        )
        multimodal_rows.append(
            {
                "claim_id": email_row["claim_id"],
                "email_id": email_row["email_id"],
                "scenario_name": scenario_name,
                "text_source": "data/sample/claims/claim_email_ham_spam_sample.csv",
                "tabular_source": "data/sample/claims/claim_history_sample.csv",
                "evidence_path": relative_evidence_path,
                "item_category": email_row["device_category"],
                "incident_type": email_row["incident_type"],
                "text_label": email_row["label"],
                "document_label": evidence_rows[-1]["document_label"],
                "overall_risk_label": risk_label,
                "email_language_risk_score": claim_rows[-1]["email_language_risk_score"],
                "behavioural_risk_score": claim_rows[-1]["behavioural_risk_score"],
                "document_risk_score": claim_rows[-1]["document_risk_score"],
            }
        )

    write_csv(CLAIMS_DIR / "claim_email_ham_spam_sample.csv", email_rows, list(email_rows[0].keys()))
    write_csv(CLAIMS_DIR / "claim_history_sample.csv", claim_rows, CLAIM_HISTORY_COLUMNS)
    write_csv(MANIFEST_DIR / "evidence_manifest_sample.csv", evidence_rows, list(evidence_rows[0].keys()))
    write_csv(MANIFEST_DIR / "multimodal_sample_index.csv", multimodal_rows, list(multimodal_rows[0].keys()))

    print(f"Wrote multimodal sample pack to {SAMPLE_ROOT}")
    print(f"Claims: {len(claim_rows)}")
    print(f"Evidence manifest rows: {len(evidence_rows)}")


if __name__ == "__main__":
    main()
