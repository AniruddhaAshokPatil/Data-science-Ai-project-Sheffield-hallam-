# Issue Alignment

Audit date: 2026-04-22

This document regenerates Issues `1` to `30` so they match the current repository implementation only.

The tracked project is `ShieldWise`, an insurance claim fraud detection platform with:

- a FastAPI backend in `src/api/`
- a React frontend in `src/frontend/`
- insurance claim submission and dashboard workflows
- optional evidence upload and document-risk checks
- claim-language risk scoring
- behavioural claim-risk scoring
- live alert streaming through WebSockets
- regression tests in `tests/test_api_insurance.py`

The source of truth for these issues is the code and tests currently present in `main`, not older transaction-only or generic multimodal plans.

Each issue below uses the same structure:

- `Issue Number`
- `Issue Title`
- `Issue Objective`
- `Issue Description`
- `Key Inputs / Project Assets`
- `Deliverables`
- `Acceptance Criteria`
- `Current Repo Evidence`
- `Status Alignment`

## Current Project Data and Asset Context

### Main Structured Insurance Data

- `data/raw/insurance_claims/claim_history_detailed.csv`
- `data/raw/insurance_claims/submitted_claims.csv`

These support the insurance dashboards, claim history, and backend workflow.

### NLP Data

- `data/raw/nlp/claim_email_ham_spam.csv`

This supports the claim-language risk workflow. It should be described as a project dataset used for prototype NLP scoring, not as a validated real-world insurer communication benchmark.

### Evidence / CV Assets

- `Datasets/Receipt_Fraud_Dataset/`
- `backend/receipts_models/`
- `backend/saved_models/`

These support receipt and document-risk research assets retained in the repository. The current API document-risk flow is intentionally lightweight and rule-based at runtime, even though supporting model artifacts remain in the repository.

### Runtime and Delivery Assets

- `src/api/`
- `src/frontend/`
- `tests/test_api_insurance.py`
- `run_all.sh`
- `scripts/train_claim_email_nlp_model.py`
- `scripts/rebuild_missing_models.py`
- `scripts/validate_project.py`

## ISSUE 1

**Issue Number**  
`1`

**Issue Title**  
Prepare the Insurance Claim NLP Dataset

**Issue Objective**  
Create a clean, model-ready text dataset for claim-language risk analysis.

**Issue Description**  
This issue covers preparing the insurance claim email and claim-language dataset used by the NLP component. The workflow should clean and normalise text, preserve useful fraud cues such as urgency language and payment-change phrasing, and convert the text into a stable form for model training and inference.

**Key Inputs / Project Assets**
- `data/raw/nlp/claim_email_ham_spam.csv`
- `src/data/preprocess_nlp.py`

**Deliverables**
- Cleaned text dataset
- Reproducible preprocessing script
- Processed NLP output files

**Acceptance Criteria**
- No empty or invalid text rows remain in the processed dataset
- Preprocessing is reproducible from code
- Cleaned output can be consumed by the NLP training workflow

**Current Repo Evidence**
- `src/data/preprocess_nlp.py`
- `data/processed/nlp/`

**Status Alignment**
- Implemented in a project-specific form

## ISSUE 2

**Issue Number**  
`2`

**Issue Title**  
Document the Claim Email Ham/Spam Dataset

**Issue Objective**  
Clearly define the text dataset used for claim-language classification.

**Issue Description**  
This issue covers documenting the claim email ham/spam dataset used by the project. The dataset should be described in terms of labels, storage path, preprocessing path, and intended use in claim-language risk scoring. Any limitations in realism or generalisability should be stated honestly in the report and README.

**Key Inputs / Project Assets**
- `data/raw/nlp/claim_email_ham_spam.csv`
- `scripts/train_claim_email_nlp_model.py`

**Deliverables**
- Dataset note
- Label explanation
- Path and usage documentation

**Acceptance Criteria**
- Dataset location is clear
- Label meaning is documented
- Dataset can be traced to the NLP training pipeline

**Current Repo Evidence**
- `data/raw/nlp/claim_email_ham_spam.csv`
- `scripts/validate_project.py`

**Status Alignment**
- Implemented partially through code and repo structure, but description quality depends on project documentation

## ISSUE 3

**Issue Number**  
`3`

**Issue Title**  
Prepare the Receipt Evidence Image Dataset

**Issue Objective**  
Prepare receipt images for evidence-related CV experimentation and supporting assets.

**Issue Description**  
This issue covers preparing the receipt evidence dataset used by the repository’s supporting CV assets. It includes image organisation, resizing, normalisation, and dataset splitting needed for the retained receipt-model training and evaluation workflow.

**Key Inputs / Project Assets**
- `Datasets/Receipt_Fraud_Dataset/`
- `scripts/rebuild_missing_models.py`

**Deliverables**
- Prepared image dataset
- Reproducible preprocessing path
- Train/validation/test organisation

**Acceptance Criteria**
- Images are available in a consistent structure
- Preprocessing is reproducible
- The downstream receipt-model rebuild script can use the dataset

**Current Repo Evidence**
- `Datasets/Receipt_Fraud_Dataset/`
- `backend/receipts_models/`

**Status Alignment**
- Supporting implementation present

## ISSUE 4

**Issue Number**  
`4`

**Issue Title**  
Document the Receipt Fraud Dataset

**Issue Objective**  
Explain the image dataset used for receipt-focused research assets in the repository.

**Issue Description**  
This issue covers documenting the receipt dataset retained in the repository for evidence-analysis experimentation. The documentation should explain what the dataset contains, how it is used by the rebuild script, and how it relates to the lightweight document-risk flow currently used in the running API.

**Key Inputs / Project Assets**
- `Datasets/Receipt_Fraud_Dataset/`
- `scripts/rebuild_missing_models.py`

**Deliverables**
- Dataset description
- Usage note
- Link to training or rebuild workflow

**Acceptance Criteria**
- Dataset purpose is documented clearly
- The distinction between retained research assets and active runtime logic is clear

**Current Repo Evidence**
- `Datasets/Receipt_Fraud_Dataset/README.dataset.txt`
- `Datasets/Receipt_Fraud_Dataset/README.roboflow.txt`

**Status Alignment**
- Implemented partially through retained assets

## ISSUE 5

**Issue Number**  
`5`

**Issue Title**  
Create a Safe Train/Test Split for NLP and Supporting CV Work

**Issue Objective**  
Reduce leakage and keep model evaluation credible.

**Issue Description**  
This issue covers ensuring that the NLP and supporting receipt-image workflows use clean and reproducible train/test separation. The split logic should avoid overlap between training and testing examples and should be traceable from script outputs.

**Key Inputs / Project Assets**
- `scripts/train_claim_email_nlp_model.py`
- `scripts/rebuild_missing_models.py`

**Deliverables**
- Reproducible split strategy
- Train/test or train/validation/test outputs

**Acceptance Criteria**
- Split logic is explicit in code
- Test examples are not reused in training

**Current Repo Evidence**
- `scripts/train_claim_email_nlp_model.py`
- `backend/saved_models/nlp_metrics.json`
- `backend/receipts_models/cv_metrics.json`

**Status Alignment**
- Implemented in supporting model scripts

## ISSUE 6

**Issue Number**  
`6`

**Issue Title**  
Encode Structured Insurance Claim Fields

**Issue Objective**  
Prepare structured insurance claim fields for analysis and scoring.

**Issue Description**  
This issue covers preparing structured insurance claim attributes such as policy type, incident type, item category, and related claim context fields so they can support the behavioural risk workflow and dashboard summaries.

**Key Inputs / Project Assets**
- `data/raw/insurance_claims/claim_history_detailed.csv`
- `src/api/services/insurance_data.py`

**Deliverables**
- Standardised structured fields
- Consistent field handling logic

**Acceptance Criteria**
- Core structured fields are usable in the backend workflow
- Field meaning remains explainable in the project narrative

**Current Repo Evidence**
- `src/api/services/insurance_data.py`

**Status Alignment**
- Implemented mainly through backend logic rather than a standalone encoding pipeline

## ISSUE 7

**Issue Number**  
`7`

**Issue Title**  
Engineer Behavioural Claim-Risk Features

**Issue Objective**  
Create fraud-relevant claim behaviour features for structured risk scoring.

**Issue Description**  
This issue covers engineering and applying behavioural fraud indicators such as prior claims count, recent account changes, unusual claim patterns, and claim amount ratios. These features support the structured claim-risk component of the project.

**Key Inputs / Project Assets**
- Claim submission fields
- `src/api/services/insurance_data.py`

**Deliverables**
- Behavioural risk feature logic
- Risk-scoring rules or derived values

**Acceptance Criteria**
- Features are meaningful in the insurance claim context
- Features contribute to the overall risk output

**Current Repo Evidence**
- `src/api/services/insurance_data.py`
- `tests/test_api_insurance.py`

**Status Alignment**
- Implemented

## ISSUE 8

**Issue Number**  
`8`

**Issue Title**  
Clean Missing Values and Sparse Insurance Fields

**Issue Objective**  
Improve data quality for the active insurance workflow.

**Issue Description**  
This issue covers handling missing values and sparse fields in the insurance data used by the dashboards and backend services. The goal is to keep the project stable and interpretable without relying on noisy or unusable fields.

**Key Inputs / Project Assets**
- `data/raw/insurance_claims/claim_history_detailed.csv`
- `src/api/services/insurance_data.py`

**Deliverables**
- Stable data preparation logic
- Missing-field handling rules

**Acceptance Criteria**
- Required runtime fields are present or safely defaulted
- Backend workflow does not fail on common missing-field cases

**Current Repo Evidence**
- `src/api/services/insurance_data.py`
- `src/api/services/insurance_dashboard.py`

**Status Alignment**
- Implemented through runtime preparation logic

## ISSUE 9

**Issue Number**  
`9`

**Issue Title**  
Merge Static and Submitted Insurance Claim Records

**Issue Objective**  
Combine the base insurance dataset with newly submitted claims.

**Issue Description**  
This issue covers joining the static insurance claim history with user-submitted runtime claims so the dashboards always reflect both seeded data and newly created claims.

**Key Inputs / Project Assets**
- `data/raw/insurance_claims/claim_history_detailed.csv`
- runtime database tables

**Deliverables**
- Unified claim history view
- Merged dashboard-ready dataset

**Acceptance Criteria**
- Submitted claims appear in the customer and investigator views
- Merge logic preserves required fields

**Current Repo Evidence**
- `src/api/services/insurance_data.py`
- `src/api/db.py`

**Status Alignment**
- Implemented

## ISSUE 10

**Issue Number**  
`10`

**Issue Title**  
Prepare the Main Insurance Claim Dataset

**Issue Objective**  
Establish the core structured insurance dataset used by the application.

**Issue Description**  
This issue covers preparing and maintaining the main insurance claim history dataset used by the active project. It supports dashboards, seeded examples, and the broader insurance submission narrative.

**Key Inputs / Project Assets**
- `data/raw/insurance_claims/claim_history_detailed.csv`

**Deliverables**
- Main claim dataset
- Basic field documentation

**Acceptance Criteria**
- Dataset is loadable by the backend
- Dataset supports the dashboard and service workflows

**Current Repo Evidence**
- `src/api/config.py`
- `docs/PROJECT_TRACEABILITY.md`

**Status Alignment**
- Implemented

## ISSUE 11

**Issue Number**  
`11`

**Issue Title**  
Create the Risk Register and Risk Heat Map

**Issue Objective**  
Capture project delivery, modelling, and ethics risks.

**Issue Description**  
This issue covers documenting risks such as false positives, limited model realism, lightweight document checks, supporting-model limitations, and the gap between prototype scoring and real insurer operations.

**Key Inputs / Project Assets**
- Full project scope

**Deliverables**
- Risk register
- Risk heat map

**Acceptance Criteria**
- Technical and ethical risks are documented clearly
- Impact and likelihood are assessed

**Current Repo Evidence**
- Governance output not tracked directly in runtime code

**Status Alignment**
- Planning and submission activity, not an implemented runtime feature

## ISSUE 12

**Issue Number**  
`12`

**Issue Title**  
Create the RACI Matrix

**Issue Objective**  
Define responsibility across project work areas.

**Issue Description**  
This issue covers documenting who is responsible, accountable, consulted, and informed across backend work, frontend work, data preparation, testing, reporting, and presentation.

**Key Inputs / Project Assets**
- Project work plan

**Deliverables**
- RACI matrix

**Acceptance Criteria**
- Roles are defined clearly for submission documentation

**Current Repo Evidence**
- Governance output not tracked directly in runtime code

**Status Alignment**
- Planning and submission activity

## ISSUE 13

**Issue Number**  
`13`

**Issue Title**  
Create the Gantt Chart

**Issue Objective**  
Visualise the project timeline and major milestones.

**Issue Description**  
This issue covers producing a schedule view for the insurance project, including data preparation, backend work, frontend work, testing, and final submission tasks.

**Key Inputs / Project Assets**
- Project plan

**Deliverables**
- Gantt chart

**Acceptance Criteria**
- Timeline matches the actual delivery phases of the project

**Current Repo Evidence**
- Governance output not tracked directly in runtime code

**Status Alignment**
- Planning and submission activity

## ISSUE 14

**Issue Number**  
`14`

**Issue Title**  
Create the Project Charter

**Issue Objective**  
Define scope, outcomes, and delivery boundaries for ShieldWise.

**Issue Description**  
This issue covers framing the project correctly as an insurance claim fraud detection platform with claim submission, evidence checks, risk scoring, dashboards, and live alerts.

**Key Inputs / Project Assets**
- README
- project traceability note

**Deliverables**
- Project charter

**Acceptance Criteria**
- Scope matches the repository and deliverable accurately

**Current Repo Evidence**
- `readme.md`
- `docs/PROJECT_TRACEABILITY.md`

**Status Alignment**
- Submission and planning activity

## ISSUE 15

**Issue Number**  
`15`

**Issue Title**  
Establish the Baseline Behavioural Claim-Risk Scoring Logic

**Issue Objective**  
Create an initial structured fraud-scoring baseline for the insurance workflow.

**Issue Description**  
This issue covers the baseline behavioural scoring logic used to assess claim risk from structured claim features. In the current repository this is implemented as explainable scoring logic rather than a separate production-grade tabular model.

**Key Inputs / Project Assets**
- claim submission fields
- `src/api/services/insurance_data.py`

**Deliverables**
- Baseline structured risk logic
- Testable risk outputs

**Acceptance Criteria**
- Risk output changes in response to relevant claim features
- The logic is explainable and stable

**Current Repo Evidence**
- `src/api/services/insurance_data.py`
- `tests/test_api_insurance.py`

**Status Alignment**
- Implemented in rule-based form

## ISSUE 16

**Issue Number**  
`16`

**Issue Title**  
Refine the Claim-Risk Scoring Rules

**Issue Objective**  
Improve the quality and separation of the behavioural scoring component.

**Issue Description**  
This issue covers refining the weights, thresholds, and decision logic used in the structured insurance risk workflow so the claim scoring is more realistic and easier to justify in the final submission.

**Key Inputs / Project Assets**
- `src/api/services/insurance_data.py`
- regression tests

**Deliverables**
- Improved risk-scoring logic
- Updated tests where needed

**Acceptance Criteria**
- The scoring remains deterministic and testable
- Changes improve clarity or separation of low/medium/high risk cases

**Current Repo Evidence**
- `src/api/services/insurance_data.py`

**Status Alignment**
- Implemented and refined in code

## ISSUE 17

**Issue Number**  
`17`

**Issue Title**  
Retain Supporting Anomaly or Outlier Detection Assets

**Issue Objective**  
Preserve supporting experimental artefacts without making them the main submission surface.

**Issue Description**  
This issue covers the repository’s retained supporting model assets for broader fraud experimentation. In the current submission they are not the main runtime path, but they remain part of the background modelling work.

**Key Inputs / Project Assets**
- `backend/saved_models/ocsvm.pkl`

**Deliverables**
- Supporting artefact retained and documented appropriately

**Acceptance Criteria**
- Supporting assets are clearly distinguished from the active runtime workflow

**Current Repo Evidence**
- `backend/saved_models/ocsvm.pkl`

**Status Alignment**
- Supporting research asset only

## ISSUE 18

**Issue Number**  
`18`

**Issue Title**  
Support Document and Receipt Evidence Analysis

**Issue Objective**  
Provide the evidence-analysis component of the insurance workflow.

**Issue Description**  
This issue covers the project’s document and receipt evidence analysis path. In the current running API, document-risk scoring is lightweight and rule-based, focusing on duplicate evidence detection, image readability, image size, aspect ratio, palette checks, and basic PDF characteristics. Supporting receipt-model artefacts remain in the repository as research assets, but the live API relies on the runtime checks implemented in the service layer.

**Key Inputs / Project Assets**
- uploaded evidence files
- `src/api/services/document_risk.py`
- supporting receipt model assets

**Deliverables**
- Evidence upload analysis
- Document-risk score
- Evidence summary for dashboards

**Acceptance Criteria**
- Uploaded files are accepted or rejected safely
- Risk summaries are generated consistently
- Duplicate receipt detection works

**Current Repo Evidence**
- `src/api/services/document_risk.py`
- `tests/test_api_insurance.py`

**Status Alignment**
- Implemented in runtime service logic

## ISSUE 19

**Issue Number**  
`19`

**Issue Title**  
Train and Integrate the Claim-Language Risk Model

**Issue Objective**  
Provide the NLP component used for email or claim-language risk scoring.

**Issue Description**  
This issue covers the NLP training workflow and the claim-language scoring logic used in the insurance platform. The repository includes training scripts and saved model artefacts, and the runtime scoring path uses that work to separate more genuine claim language from suspicious claim language.

**Key Inputs / Project Assets**
- `data/raw/nlp/claim_email_ham_spam.csv`
- `scripts/train_claim_email_nlp_model.py`
- `backend/saved_models/`

**Deliverables**
- Trained NLP pipeline
- Saved model artefacts
- Runtime scoring logic

**Acceptance Criteria**
- NLP scoring distinguishes stronger genuine vs suspicious examples
- Model files are loadable by the service layer

**Current Repo Evidence**
- `scripts/train_claim_email_nlp_model.py`
- `src/api/services/insurance_data.py`
- `backend/saved_models/nlp_metrics.json`

**Status Alignment**
- Implemented

## ISSUE 20

**Issue Number**  
`20`

**Issue Title**  
Set Up the FastAPI Backend Skeleton

**Issue Objective**  
Create the backend service structure for the live insurance application.

**Issue Description**  
This issue covers the FastAPI application setup, including app startup, routing, middleware, health checks, authentication wiring, and service registration.

**Key Inputs / Project Assets**
- `src/api/main.py`
- `src/api/routers/`
- `src/api/services/`

**Deliverables**
- Running FastAPI app
- Structured API module layout

**Acceptance Criteria**
- App starts successfully
- Routes are organised clearly

**Current Repo Evidence**
- `src/api/main.py`
- `src/api/routers/health.py`
- `src/api/routers/auth.py`
- `src/api/routers/insurance.py`

**Status Alignment**
- Implemented

## ISSUE 21

**Issue Number**  
`21`

**Issue Title**  
Add Insurance Claim Prediction and Submission Endpoints

**Issue Objective**  
Expose the insurance workflow through backend endpoints.

**Issue Description**  
This issue covers the backend endpoints that accept claims, calculate risk signals, return dashboard-ready outputs, and support evidence upload. In the current repo these are insurance-specific endpoints rather than generic tabular/CV/NLP standalone APIs.

**Key Inputs / Project Assets**
- `src/api/routers/insurance.py`
- service layer

**Deliverables**
- Claim submission endpoints
- Evidence submission endpoint
- Dashboard endpoints

**Acceptance Criteria**
- Endpoints return valid insurance workflow responses
- Risk outputs are included where expected

**Current Repo Evidence**
- `src/api/routers/insurance.py`

**Status Alignment**
- Implemented

## ISSUE 22

**Issue Number**  
`22`

**Issue Title**  
Implement the WebSocket Alert Stream

**Issue Objective**  
Enable live investigator alerts in the running application.

**Issue Description**  
This issue covers the backend WebSocket stream used to push claim alerts and queue updates without manual refresh.

**Key Inputs / Project Assets**
- `src/api/websocket_manager.py`
- `src/api/main.py`

**Deliverables**
- WebSocket alert endpoint
- Alert stream manager

**Acceptance Criteria**
- Authenticated clients can receive live alert events

**Current Repo Evidence**
- `src/api/websocket_manager.py`
- `src/api/main.py`

**Status Alignment**
- Implemented

## ISSUE 23

**Issue Number**  
`23`

**Issue Title**  
Create the React Frontend Skeleton

**Issue Objective**  
Provide the frontend structure for the ShieldWise web app.

**Issue Description**  
This issue covers the React and Vite frontend setup used by the insurance application, including the root app, entry files, and initial layout foundation.

**Key Inputs / Project Assets**
- `src/frontend/package.json`
- `src/frontend/src/main.jsx`
- `src/frontend/src/App.jsx`

**Deliverables**
- Running frontend application
- Frontend entry structure

**Acceptance Criteria**
- Frontend starts successfully
- Main app shell renders

**Current Repo Evidence**
- `src/frontend/src/main.jsx`
- `src/frontend/index.html`

**Status Alignment**
- Implemented

## ISSUE 24

**Issue Number**  
`24`

**Issue Title**  
Build the Insurance Fraud Monitoring Dashboard

**Issue Objective**  
Create the customer and investigator dashboard experience.

**Issue Description**  
This issue covers the main UI views for the public homepage, customer dashboard, investigator queue, claim summaries, evidence summaries, and risk-monitoring panels.

**Key Inputs / Project Assets**
- frontend application code
- backend dashboard responses

**Deliverables**
- Dashboard UI components
- Insurance workflow views

**Acceptance Criteria**
- Users can see claims, queue items, and summary metrics in the UI

**Current Repo Evidence**
- `src/frontend/src/App.jsx`
- `src/frontend/src/styles.css`

**Status Alignment**
- Implemented

## ISSUE 25

**Issue Number**  
`25`

**Issue Title**  
Connect the Frontend to the WebSocket Stream

**Issue Objective**  
Display live alerts in the investigator-facing UI.

**Issue Description**  
This issue covers integrating the React frontend with the backend WebSocket alert stream so live alerts appear in the running application.

**Key Inputs / Project Assets**
- frontend WebSocket client logic
- backend WebSocket endpoint

**Deliverables**
- Working frontend alert stream integration

**Acceptance Criteria**
- Live alerts are rendered in the frontend

**Current Repo Evidence**
- `src/frontend/src/App.jsx`
- `src/api/main.py`

**Status Alignment**
- Implemented

## ISSUE 26

**Issue Number**  
`26`

**Issue Title**  
Run End-to-End Integration Tests for the Insurance Workflow

**Issue Objective**  
Validate the full ShieldWise workflow from login through claim monitoring.

**Issue Description**  
This issue covers integration-style testing of authentication, claim submission, evidence upload, risk scoring, dashboard output, and alert streaming behaviour.

**Key Inputs / Project Assets**
- API application
- regression tests

**Deliverables**
- Test suite
- Verification of main user journeys

**Acceptance Criteria**
- Core insurance flows pass automated tests

**Current Repo Evidence**
- `tests/test_api_insurance.py`

**Status Alignment**
- Implemented

## ISSUE 27

**Issue Number**  
`27`

**Issue Title**  
Prepare Model Evaluation and Visualisation Outputs

**Issue Objective**  
Support the final report and demonstration with model evidence.

**Issue Description**  
This issue covers the retained metrics, notebooks, and model evaluation outputs that support discussion of the NLP and evidence-analysis components in the final submission.

**Key Inputs / Project Assets**
- saved model metrics
- notebooks in `backend/`

**Deliverables**
- Evaluation outputs
- Visualisation or notebook evidence

**Acceptance Criteria**
- Metrics can be referenced in the report
- Supporting outputs align with retained artefacts

**Current Repo Evidence**
- `backend/saved_models/nlp_metrics.json`
- `backend/receipts_models/cv_metrics.json`
- `backend/*.ipynb`

**Status Alignment**
- Partially implemented through retained assets

## ISSUE 28

**Issue Number**  
`28`

**Issue Title**  
Write the Ethics and Responsible AI Section

**Issue Objective**  
Explain the responsible use and limitations of the ShieldWise system.

**Issue Description**  
This issue covers documenting fairness concerns, false positives, explainability, evidence handling, and the distinction between a student project prototype and real-world insurer decision-making systems.

**Key Inputs / Project Assets**
- project behaviour
- README and docs

**Deliverables**
- Ethics and responsible AI write-up

**Acceptance Criteria**
- Risks and limitations are documented honestly

**Current Repo Evidence**
- Mentioned indirectly in project docs, not yet a standalone strong section

**Status Alignment**
- Partially complete in documentation terms

## ISSUE 29

**Issue Number**  
`29`

**Issue Title**  
Write the Final Report

**Issue Objective**  
Produce the final written submission for the insurance project.

**Issue Description**  
This issue covers writing the report that explains the insurance fraud problem, project architecture, data preparation, runtime logic, tests, results, limitations, and conclusions.

**Key Inputs / Project Assets**
- full repository

**Deliverables**
- Final written report

**Acceptance Criteria**
- Report accurately reflects the repository and implemented features

**Current Repo Evidence**
- Final report not tracked in repository source files

**Status Alignment**
- Submission activity outside main runtime code

## ISSUE 30

**Issue Number**  
`30`

**Issue Title**  
Prepare the Presentation Slides and Demo

**Issue Objective**  
Create the final presentation and walkthrough of the ShieldWise application.

**Issue Description**  
This issue covers preparing the slide deck and live demo flow so the final delivery shows the customer login, claim submission, evidence upload, investigator dashboard, and live alert stream clearly.

**Key Inputs / Project Assets**
- running application
- supporting documentation

**Deliverables**
- Slide deck
- Demo walkthrough

**Acceptance Criteria**
- Presentation aligns with the implemented application
- Demo flow is coherent and repeatable

**Current Repo Evidence**
- Presentation assets not tracked directly in repository

**Status Alignment**
- Submission activity outside main runtime code

## Alignment Rule

If any older issue title, draft note, or planning text disagrees with the running code, the codebase and tests take priority. This file should stay aligned to the actual implementation in:

- `src/api/`
- `src/frontend/`
- `tests/test_api_insurance.py`
