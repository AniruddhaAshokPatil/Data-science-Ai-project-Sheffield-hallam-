# ShieldWise

ShieldWise is a submission-ready insurance claim fraud detection project. It combines:

- a FastAPI backend for claim intake, dashboards, evidence analysis, and live alerts
- a React frontend for the public homepage, policyholder dashboard, and investigator dashboard
- a legacy Streamlit multimodal demo that still showcases the saved NLP and computer-vision models in `backend/`

The current tracked product direction is the insurance workflow in `src/api/` and `src/frontend/`. The Streamlit app in `App_Frontend.py` is retained as a model workbench, not the primary product surface.

## What The Project Does

- Accepts insurance claims with structured form data and optional receipt evidence
- Scores claim language, uploaded documents, and behavioural risk signals
- Shows a customer-facing dashboard for submitted claims
- Shows an investigator dashboard with a queue and live alert feed
- Persists submitted claims in a local SQLite runtime database

## Main Stack

- Backend: FastAPI
- Frontend: React + Vite
- Realtime alerts: WebSocket
- Data layer: pandas + SQLite
- Optional demo app: Streamlit

## Repository Structure

```text
.
├── App_Frontend.py                 # Legacy multimodal Streamlit demo
├── backend/                        # Saved NLP, receipt CV, and ID-card model artifacts
├── data/
│   ├── raw/insurance_claims/       # Main insurance datasets used by the API
│   ├── raw/nlp/                    # Supporting NLP datasets
│   ├── raw/transactions/           # Supporting transaction datasets
│   └── processed/                  # Local processed outputs and runtime DB
├── docs/
│   ├── ISSUE_ALIGNMENT.md
│   ├── INSURANCE_CLAIM_SAMPLES.md
│   └── PROJECT_TRACEABILITY.md
├── scripts/
│   ├── rebuild_missing_models.py
│   ├── train_claim_email_nlp_model.py
│   ├── train_transaction_fraud_model.py
│   └── validate_project.py
├── src/
│   ├── api/                        # FastAPI application
│   └── frontend/                   # React/Vite frontend
└── tests/
    └── test_api_insurance.py       # API regression tests
```

## How To Run

### Option 1: Run The Full Local Stack

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm

cd src/frontend
npm install
cd ../..

chmod +x run_all.sh
./run_all.sh
```

This starts:

- React: `http://localhost:5173`
- FastAPI: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Streamlit: `http://localhost:8501`

### Option 2: Run Only The Insurance Web App

Backend:

```bash
source .venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd src/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### Option 3: Run Only The Legacy Streamlit Demo

```bash
source .venv/bin/activate
streamlit run App_Frontend.py
```

## Demo Accounts

The API seeds local demo users on startup:

- Policyholder: `demo_user` / `UserPass123!`
- Investigator: `investigator_anna` / `InvestigatorPass123!`

Policyholder claim submissions are now identity-bound to the signed-in customer account.

## Testing

Run the insurance API tests with:

```bash
python3 -m pytest tests/test_api_insurance.py
```

Run the project health check with:

```bash
python3 scripts/validate_project.py
```

## Submission Notes

- The primary submission surface is the ShieldWise insurance platform in `src/api/` and `src/frontend/`.
- The Streamlit app is preserved because it still demonstrates the saved multimodal models included in the repository.
- Legacy duplicate planning material and stale draft folders were removed so the repository reflects the current deliverable more clearly.

## Supporting Files

- [docs/PROJECT_TRACEABILITY.md](docs/PROJECT_TRACEABILITY.md)
- [docs/ISSUE_ALIGNMENT.md](docs/ISSUE_ALIGNMENT.md)
- [docs/INSURANCE_CLAIM_SAMPLES.md](docs/INSURANCE_CLAIM_SAMPLES.md)
