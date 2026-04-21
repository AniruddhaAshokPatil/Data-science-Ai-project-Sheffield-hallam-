# Project Traceability

Audit date: 2026-04-21

This note records what is actually tracked in the repository after cleanup. I use it as the ground truth for the submission narrative so the README, issue notes, and codebase all describe the same project.

## Current Project Shape

The repository now has two clearly separated parts:

1. `ShieldWise`, the tracked insurance claim fraud platform
2. the older `App_Frontend.py` Streamlit model demo

The insurance platform is the primary deliverable and consists of:

- FastAPI application code in `src/api/`
- React frontend code in `src/frontend/`
- regression tests in `tests/test_api_insurance.py`
- insurance datasets in `data/raw/insurance_claims/`

The Streamlit app remains because it still uses the tracked saved model files in `backend/`.

## Active Runtime Paths

| Path | Role | Status |
| --- | --- | --- |
| `src/api/` | Main backend for the current project | Active |
| `src/frontend/` | Main frontend for the current project | Active |
| `tests/test_api_insurance.py` | API regression coverage | Active |
| `data/raw/insurance_claims/` | Main input data for the insurance workflow | Active |
| `data/processed/shieldwise_runtime.db` | Local runtime state during demos | Generated locally |
| `App_Frontend.py` | Legacy Streamlit demo for saved models | Retained secondary app |
| `backend/receipts_models/` | Receipt CV model artifacts used by Streamlit | Active for demo |
| `backend/saved_models/` | NLP, transaction, and ID-card artifacts used by Streamlit and scripts | Active for demo/training support |

## Cleanup Decisions

The following legacy materials were removed because they were not part of the current deliverable:

- `Initial Work/`
- old `.docx` submission files in the repo root
- `docs/FRONTEND_ISSUE_ALIGNMENT.md`

I removed them because they duplicated older planning or draft material without contributing to the current runnable submission.

## Current Execution Story

The repository supports these execution paths:

### ShieldWise web app

- `uvicorn src.api.main:app --reload`
- `npm run dev` in `src/frontend/`

### All-in-one local demo

- `./run_all.sh`

### Legacy Streamlit demo

- `streamlit run App_Frontend.py`

## Key Behavioural Trace Points

These files represent the most important submission logic:

- `src/api/routers/insurance.py`
- `src/api/services/insurance_dashboard.py`
- `src/api/services/insurance_data.py`
- `src/api/services/document_risk.py`
- `src/api/auth.py`
- `src/frontend/src/App.jsx`

## Identity Integrity Note

During cleanup I also tightened the claim-submission flow so a normal policyholder submits claims as the signed-in account identity rather than arbitrary form-entered name and email values. That behaviour is now covered in `tests/test_api_insurance.py`.

## Ground Rule

If older notes, issue text, and tracked files disagree, I treat the tracked files and runnable tests as the source of truth. This document should stay aligned with the code that is actually present in `main`.
