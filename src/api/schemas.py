from typing import List

from pydantic import BaseModel, Field


class FeatureCard(BaseModel):
    name: str
    description: str


class PublicFeature(BaseModel):
    title: str
    text: str


class ClaimEmailSample(BaseModel):
    subject: str
    body: str


class AlertItem(BaseModel):
    id: str
    time: str
    severity: str
    title: str
    detail: str


class QueueItem(BaseModel):
    claim_id: str
    claimant: str
    policy_type: str
    amount: str
    submitted_at: str = ""
    nlp_risk: float
    document_risk: float
    behavioural_risk: float
    combined_risk: str
    alert_reason: str


class CustomerClaim(BaseModel):
    claim_id: str
    policy_type: str
    item_category: str
    amount: str
    status: str
    submitted_at: str
    risk_summary: str
    next_step: str
    evidence_name: str = ""
    evidence_status: str = ""


class HomeResponse(BaseModel):
    metrics: dict
    public_features: List[PublicFeature]
    behavioural_fields: List[FeatureCard]
    claim_email_samples: dict[str, ClaimEmailSample]
    live_alerts: List[AlertItem]


class CustomerDashboardResponse(BaseModel):
    claims: List[CustomerClaim]


class CompanyDashboardResponse(BaseModel):
    metrics: dict
    queue: List[QueueItem]
    live_alerts: List[AlertItem]


class ClaimSubmissionRequest(BaseModel):
    claimant_name: str = Field(min_length=2, max_length=100)
    claimant_email: str = Field(min_length=5, max_length=120)
    policy_type: str = Field(min_length=3, max_length=40)
    coverage_tier: str = Field(min_length=3, max_length=40)
    item_category: str = Field(min_length=2, max_length=60)
    incident_type: str = Field(min_length=3, max_length=60)
    claim_amount_gbp: float = Field(gt=0)
    estimated_item_value_gbp: float = Field(gt=0)
    prior_claims_count: int = Field(ge=0, le=20)
    claims_last_12_months: int = Field(ge=0, le=20)
    days_since_policy_start: int = Field(ge=0, le=3650)
    recent_high_value_purchase_flag: bool = False
    unusual_spend_spike_flag: bool = False
    account_login_location_change_flag: bool = False
    multiple_devices_last_7_days_flag: bool = False
    address_change_last_30_days_flag: bool = False
    phone_change_last_30_days_flag: bool = False
    bank_detail_change_last_30_days_flag: bool = False
    late_night_submission_flag: bool = False
    weekend_submission_flag: bool = False
    receipt_present_flag: bool = True
    receipt_mismatch_flag: bool = False
    duplicate_receipt_flag: bool = False
    image_tamper_flag: bool = False
    claim_story: str = Field(min_length=20, max_length=3000)


class ClaimSubmissionResponse(BaseModel):
    claim_id: str
    customer_claim: CustomerClaim
    queue_item: QueueItem
    alert: AlertItem
    evidence_summary: dict


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    full_name: str
    email: str
