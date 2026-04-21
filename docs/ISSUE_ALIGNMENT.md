# Issue Alignment

Audit date: 2026-04-21

This file maps the repository to the GitHub issue history as it stands after cleanup. The goal is not to preserve every historical assumption. The goal is to show which issues still match the tracked project and which ones should be updated or closed out manually on GitHub.

## Current Alignment Summary

The repository now clearly supports these issue themes:

- insurance frontend and backend implementation
- authentication and role-aware dashboards
- claim submission with evidence upload
- live alert streaming
- API regression testing
- supporting insurance-focused model-training and demo artifacts

## Issues That Match The Current Repo Well

| Issue | Alignment | Evidence |
| --- | --- | --- |
| `#20 Set Up FastAPI Backend Skeleton` | Implemented | `src/api/main.py`, `src/api/routers/`, `src/api/services/` |
| `#21 Add Prediction Endpoints for Tabular, CV, NLP Models` | Partially implemented in a product-specific form | `src/api/routers/insurance.py`, `src/api/services/document_risk.py`, `src/api/services/insurance_data.py` |
| `#22 Implement WebSocket Alert Stream in Backend` | Implemented | `src/api/websocket_manager.py`, `src/api/main.py` |
| `#23 Create React Frontend Skeleton` | Implemented | `src/frontend/index.html`, `src/frontend/package.json`, `src/frontend/src/main.jsx`, `src/frontend/src/App.jsx` |
| `#24 Build Fraud Monitoring Dashboard Components` | Implemented | `src/frontend/src/App.jsx`, `src/frontend/src/styles.css` |
| `#25 Connect Frontend to WebSocket Alert Stream` | Implemented | `src/frontend/src/App.jsx`, `src/api/main.py`, `src/api/websocket_manager.py` |
| `#26 End-to-End Integration Test (Backend + Frontend + Models)` | Partially implemented | `tests/test_api_insurance.py` covers backend workflow, but no browser-level E2E suite is tracked |
| `#28 Ethics & Responsible AI Section` | Partially implemented | `readme.md`, `docs/INSURANCE_CLAIM_SAMPLES.md` |

## Issues That No Longer Match The Primary Submission Story

These issue groups describe older or broader experimentation that no longer represent the tracked submission:

| Issue Area | Current position |
| --- | --- |
| Transaction-only fraud pipeline issues | Retired from the tracked repository and no longer part of the main web product |
| Streamlit-only direction | No longer the primary repo narrative; Streamlit is now a secondary demo surface |
| Older planning/reporting issues | Many are not represented by current tracked source files after cleanup |

## Manual GitHub Issue Edits Recommended

If you want the GitHub issue tracker to match the cleaned repository, these are the edits I recommend making directly on GitHub:

1. Update the description of `#20`, `#21`, and `#22` so they reference the tracked insurance API and WebSocket implementation rather than transaction placeholders.
2. Close `#23`, `#24`, and `#25` as completed and attach evidence from `src/frontend/src/App.jsx`, `src/frontend/src/main.jsx`, and `src/api/main.py`.
3. Clarify `#26` as partially complete: backend workflow coverage exists in `tests/test_api_insurance.py`, but a browser-level E2E suite is still missing unless you add Playwright or Cypress later.
4. Reword `#27` so it reflects the notebooks that do exist in `backend/`, while keeping it open if you still want a more polished evaluation notebook for the report.
5. Reword `#28` so it references insurance-domain ethics and responsible AI rather than payment-regulation language from the older transaction framing.
6. Keep the older transaction issue history only as historical context, because the current tracked deliverable is the insurance workflow.

## Recommended Live Issue States

| Issue | Recommended state | Reason |
| --- | --- | --- |
| `#20` | Closed | FastAPI backend skeleton is present and in use |
| `#21` | Closed | Insurance endpoints replaced the older standalone transaction endpoint plan |
| `#22` | Closed | WebSocket alert stream is implemented at `src/api/main.py` |
| `#23` | Close now | React frontend skeleton is implemented |
| `#24` | Close now | Dashboard components are implemented |
| `#25` | Close now | Frontend WebSocket integration is implemented |
| `#26` | Keep open or relabel partial | Backend integration tests exist, but no browser E2E suite is tracked |
| `#27` | Keep open | Existing notebooks exist, but report-facing evaluation work may still be incomplete |
| `#28` | Keep open | Repo mentions ethics, but a stronger dedicated section may still be needed |
| `#29` | Keep open | Final report is not tracked in this repository |
| `#30` | Keep open | Slide deck and rehearsal evidence are not tracked in this repository |

## GitHub Tracker Status

This file is intended to stay aligned with the live GitHub tracker. If issue bodies or states drift again, update them so the tracker reflects the current insurance-focused repository rather than retired transaction-only work.
