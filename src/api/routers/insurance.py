from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.api.auth import AuthenticatedUser, require_customer_role, require_investigator_role, require_user_role
from src.api.schemas import (
    ClaimSubmissionRequest,
    ClaimSubmissionResponse,
    CompanyDashboardResponse,
    CustomerDashboardResponse,
    HomeResponse,
)
from src.api.services.insurance_dashboard import (
    build_company_dashboard_payload,
    build_customer_dashboard_payload,
    build_home_payload,
    create_submitted_claim,
)
from src.api.services.document_risk import analyze_and_store_evidence
from src.api.websocket_manager import alert_stream_manager


router = APIRouter(prefix="/api/insurance", tags=["insurance"])


@router.get("/home", response_model=HomeResponse)
def insurance_home() -> HomeResponse:
    # Public homepage data is served from the API so the frontend stays data-driven.
    return build_home_payload()


@router.get("/customer-dashboard", response_model=CustomerDashboardResponse)
def customer_dashboard(current_user: AuthenticatedUser = Depends(require_user_role)) -> CustomerDashboardResponse:
    # The policyholder dashboard only shows claims linked to the signed-in account.
    return build_customer_dashboard_payload(claimant_email=current_user.email)


@router.get("/company-dashboard", response_model=CompanyDashboardResponse)
def company_dashboard(_: AuthenticatedUser = Depends(require_investigator_role)) -> CompanyDashboardResponse:
    # Investigator-only dashboard data contains the review queue and live alert feed.
    return build_company_dashboard_payload()


@router.post("/claims", response_model=ClaimSubmissionResponse, status_code=201)
async def submit_claim(
    claim_request: ClaimSubmissionRequest,
    current_user: AuthenticatedUser = Depends(require_customer_role),
) -> ClaimSubmissionResponse:
    # The signed-in account supplies the claimant identity, rather than trusting form-entered identity fields.
    claim_request = claim_request.model_copy(
        update={
            "claimant_name": current_user.full_name,
            "claimant_email": current_user.email,
        }
    )
    response = create_submitted_claim(claim_request)
    await alert_stream_manager.broadcast_alert(response.alert)
    return response


@router.post("/claims/with-evidence", response_model=ClaimSubmissionResponse, status_code=201)
async def submit_claim_with_evidence(
    claimant_name: str = Form(...),
    claimant_email: str = Form(...),
    policy_type: str = Form(...),
    coverage_tier: str = Form(...),
    item_category: str = Form(...),
    incident_type: str = Form(...),
    claim_amount_gbp: float = Form(...),
    estimated_item_value_gbp: float = Form(...),
    prior_claims_count: int = Form(...),
    claims_last_12_months: int = Form(...),
    days_since_policy_start: int = Form(...),
    recent_high_value_purchase_flag: bool = Form(False),
    unusual_spend_spike_flag: bool = Form(False),
    account_login_location_change_flag: bool = Form(False),
    multiple_devices_last_7_days_flag: bool = Form(False),
    address_change_last_30_days_flag: bool = Form(False),
    phone_change_last_30_days_flag: bool = Form(False),
    bank_detail_change_last_30_days_flag: bool = Form(False),
    late_night_submission_flag: bool = Form(False),
    weekend_submission_flag: bool = Form(False),
    receipt_present_flag: bool = Form(True),
    receipt_mismatch_flag: bool = Form(False),
    duplicate_receipt_flag: bool = Form(False),
    image_tamper_flag: bool = Form(False),
    claim_story: str = Form(...),
    evidence_file: UploadFile | None = File(None),
    id_card_file: UploadFile | None = File(None),
    current_user: AuthenticatedUser = Depends(require_customer_role),
) -> ClaimSubmissionResponse:
    # Multipart form data allows claim details, receipt evidence, and an ID card to be submitted together.
    claim_request = ClaimSubmissionRequest(
        claimant_name=current_user.full_name,
        claimant_email=current_user.email,
        policy_type=policy_type,
        coverage_tier=coverage_tier,
        item_category=item_category,
        incident_type=incident_type,
        claim_amount_gbp=claim_amount_gbp,
        estimated_item_value_gbp=estimated_item_value_gbp,
        prior_claims_count=prior_claims_count,
        claims_last_12_months=claims_last_12_months,
        days_since_policy_start=days_since_policy_start,
        recent_high_value_purchase_flag=recent_high_value_purchase_flag,
        unusual_spend_spike_flag=unusual_spend_spike_flag,
        account_login_location_change_flag=account_login_location_change_flag,
        multiple_devices_last_7_days_flag=multiple_devices_last_7_days_flag,
        address_change_last_30_days_flag=address_change_last_30_days_flag,
        phone_change_last_30_days_flag=phone_change_last_30_days_flag,
        bank_detail_change_last_30_days_flag=bank_detail_change_last_30_days_flag,
        late_night_submission_flag=late_night_submission_flag,
        weekend_submission_flag=weekend_submission_flag,
        receipt_present_flag=receipt_present_flag,
        receipt_mismatch_flag=receipt_mismatch_flag,
        duplicate_receipt_flag=duplicate_receipt_flag,
        image_tamper_flag=image_tamper_flag,
        claim_story=claim_story,
    )
    evidence_summary = await analyze_and_store_evidence(evidence_file)
    id_card_summary = await analyze_and_store_evidence(id_card_file)
    response = create_submitted_claim(claim_request, evidence_summary=evidence_summary, id_card_summary=id_card_summary)
    await alert_stream_manager.broadcast_alert(response.alert)
    return response
