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
- supporting model-training and demo artifacts

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

These issue groups describe older or broader experimentation that still leaves artifacts in the repo, but they are not the main product being submitted now:

| Issue Area | Current position |
| --- | --- |
| Transaction-only fraud pipeline issues | Still represented in `scripts/` and `backend/saved_models/`, but not part of the main web product |
| Streamlit-only direction | No longer the primary repo narrative; Streamlit is now a secondary demo surface |
| Older planning/reporting issues | Many are not represented by current tracked source files after cleanup |

## Manual GitHub Issue Edits Recommended

If you want the GitHub issue tracker to match the cleaned repository, these are the edits I recommend making directly on GitHub:

1. Update the description of `#20`, `#21`, and `#22` so they reference the tracked insurance API and WebSocket implementation rather than missing placeholder backend files.
2. Mark `#23`, `#24`, and `#25` as complete with references to `src/frontend/src/App.jsx`.
3. Clarify `#26` as backend workflow coverage rather than a full browser E2E suite, unless you plan to add Playwright or Cypress later.
4. Reword or close any open issues that still describe the repo as lacking the React frontend or FastAPI backend, because that is no longer true.
5. Keep the model-training and dataset issues as historical context if you want to show the research path, but avoid letting them define the current submission narrative.

## Environment Limitation

I updated this alignment file locally, but I did not directly edit the GitHub issue bodies from this environment because the GitHub CLI and direct issue-edit connector access were not available in this session.
