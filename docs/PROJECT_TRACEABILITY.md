# Project Traceability

Audit date: 2026-04-21

This note records what is actually tracked in the repository after cleanup. I am using it as the ground truth for the submission narrative so the README, issue notes, and codebase all describe the same project.

## Current Project Shape

The repository now centres on one tracked product: `ShieldWise`, the insurance claim fraud platform.

The active submission consists of:

- FastAPI application code in `src/api/`
- React frontend code in `src/frontend/`
- regression tests in `tests/test_api_insurance.py`
- insurance datasets in `data/raw/insurance_claims/`
- supporting model artifacts in `backend/`

## Active Runtime Paths

| Path | Role | Status |
| --- | --- | --- |
| `src/api/` | Main backend for the current project | Active |
| `src/frontend/` | Main frontend for the current project | Active |
| `tests/test_api_insurance.py` | API regression coverage | Active |
| `data/raw/insurance_claims/` | Main input data for the insurance workflow | Active |
| `data/processed/shieldwise_runtime.db` | Local runtime state during demos | Generated locally |
| `backend/receipts_models/` | Receipt CV model artifacts that support insurance evidence scoring research | Supporting assets |
| `backend/saved_models/` | NLP and related saved model artifacts retained for supporting workflow research | Supporting assets |

## Cleanup Decisions

The following legacy materials were removed because they were not part of the current deliverable:

- `Initial Work/`
- old `.docx` submission files in the repo root
- `docs/FRONTEND_ISSUE_ALIGNMENT.md`
- transaction-only datasets in `data/raw/transactions/`
- transaction-only training script and saved model artifacts

I removed them because they duplicated older planning or draft material without contributing to the current runnable submission.

## Current Execution Story

The repository supports these execution paths:

### ShieldWise web app

- `uvicorn src.api.main:app --reload`
- `npm run dev` in `src/frontend/`

### All-in-one local demo

- `./run_all.sh`

## Key Behavioural Trace Points

These files represent the most important submission logic:

- `src/api/routers/insurance.py`
- `src/api/services/insurance_dashboard.py`
- `src/api/services/insurance_data.py`
- `src/api/services/document_risk.py`
- `src/api/auth.py`
- `src/frontend/src/App.jsx`

## Identity Integrity Note

During cleanup, the claim-submission flow was tightened so a normal policyholder submits claims as the signed-in account identity rather than arbitrary form-entered name and email values. That behaviour is now covered in `tests/test_api_insurance.py`.

## Ground Rule

If older notes, issue text, and tracked files disagree, the tracked files and runnable tests are the source of truth. This document should stay aligned with the code that is actually present in `main`.
