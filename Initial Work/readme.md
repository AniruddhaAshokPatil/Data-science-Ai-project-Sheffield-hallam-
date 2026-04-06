# Fraud Detection AI Project

<!-- I use this README as the first orientation point for myself, so it explains
     what the repository is, what the main folders do, and how to start it. -->

This repository is a multi-modal fraud detection project with:

- a FastAPI backend for transaction, NLP, analytics, and CV scoring
- model training scripts under `src/train`
- data preparation utilities under `src/data`
- a Vite/React dashboard under `src/frontend`

## Current Status

The backend now has a more production-friendly fraud API with:

- environment-driven config for version, log level, threshold, and CORS origins
- consistent API logging and JSON error handling
- stricter transaction payload validation
- automated checks for transaction, NLP, and CV API paths
- a CV dual-mode design that uses deep learning when Torch works and a clear fallback mode when it does not

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
python3 -m pip install -r requirements-dev.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Optional environment variables:

```bash
export FRAUD_APP_ENV=production
export FRAUD_APP_VERSION=1.0.0
export FRAUD_LOG_LEVEL=INFO
export FRAUD_HEURISTIC_THRESHOLD=0.65
export FRAUD_ALLOWED_ORIGINS=https://your-frontend.example.com
export FRAUD_TRUSTED_HOSTS=your-api.example.com
export FRAUD_RATE_LIMIT_REQUESTS=120
export FRAUD_RATE_LIMIT_WINDOW_SECONDS=60
```

### Frontend

```bash
cd src/frontend
npm install
npm run dev
```

### Tests

```bash
source .venv/bin/activate
python -m pytest -q
```

If I want a smaller submission-focused check, I can run:

```bash
source .venv/bin/activate
python -m pytest src/api/tests/test_end_to_end.py tests/test_transaction_scoring.py -q
```

## Health Endpoints

- `GET /health/live`: I use this for simple liveness checks.
- `GET /health/ready`: I use this for structured readiness checks, including model and artifact availability.
- I also use the readiness response to see whether CV is running in `deep_learning` mode or `heuristic_fallback` mode.

## Container Deployment

```bash
cp .env.example .env
cp src/frontend/.env.example src/frontend/.env
docker compose up --build
```

The API will be available on `http://localhost:8000` and the frontend on `http://localhost:8080`.

I keep the saved model artifacts inside the repository so the API container can
start with the same packaged assets that I verified locally.

## Release Process

I keep a dedicated release checklist in [RELEASE_CHECKLIST.md](/Users/productguru/Documents/GitHub/Data-science-Ai-project-Sheffield-hallam-/RELEASE_CHECKLIST.md) so deployment and verification steps stay repeatable.

## Submission Checklist

Before I submit the project, I use this short verification flow:

```bash
source .venv/bin/activate
python -m pytest -q
python -c "from src.api.main import app; print(app.title)"
python src/train.py --help
```

## Notes

<!-- I use this notes section to remind myself that the project is functional
     but still evolving, especially around artifacts and cleanup. -->

- The transaction, NLP, and CV routes now all return working API responses.
- The CV service is designed to prefer the full deep-learning path when Torch works, but it falls back safely when the local Torch runtime is broken.
- The repo includes trained artifacts in `src/train/artifacts` so I can demo the project without retraining first.
