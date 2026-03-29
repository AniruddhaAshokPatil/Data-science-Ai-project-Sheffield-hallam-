# Fraud Detection AI Project

<!-- I use this README as the first orientation point for myself, so it explains
     what the repository is, what the main folders do, and how to start it. -->

This repository is a multi-modal fraud detection project with:

- a FastAPI backend for transaction, NLP, analytics, and CV scoring
- model training scripts under `src/train`
- data preparation utilities under `src/data`
- a Vite/React dashboard under `src/frontend`

## Current Status

The backend now has a more production-friendly transaction API slice with:

- environment-driven config for version, log level, threshold, and CORS origins
- consistent API logging and JSON error handling
- stricter transaction payload validation
- passing automated checks for the transaction scoring path

## Quick Start

<!-- I keep the setup instructions grouped by backend, frontend, and tests
     because those are the three main ways I interact with the project. -->

### Backend

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Optional environment variables:

```bash
export FRAUD_APP_ENV=production
export FRAUD_APP_VERSION=1.0.0
export FRAUD_LOG_LEVEL=INFO
export FRAUD_HEURISTIC_THRESHOLD=0.65
export FRAUD_ALLOWED_ORIGINS=https://your-frontend.example.com
```

### Frontend

```bash
cd src/frontend
npm install
npm run dev
```

### Tests

```bash
PYTHONPATH=.venv/lib/python3.11/site-packages python3 -m pytest src/api/tests/test_end_to_end.py tests/test_transaction_scoring.py
```

## Notes

<!-- I use this notes section to remind myself that the project is functional
     but still evolving, especially around artifacts and cleanup. -->

- Some trained artifacts are present in `src/train/artifacts`, but not every model artifact exists yet.
- The transaction route is the most production-ready API slice right now; the CV, NLP, and analytics paths still need the same level of hardening.
- The repo includes generated and backup files from early experimentation, so a wider cleanup pass is still worth doing before release.
