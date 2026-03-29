# Release Checklist

I use this checklist to make releases repeatable and to avoid calling the project
"production-ready" before the operational basics are truly in place.

## Source Control

- Push the latest commit to GitHub.
- Confirm the GitHub Actions workflow passes.
- Confirm there are no accidental generated files or local-only artifacts staged for release.

## Backend

- Copy `.env.example` to `.env` and set real production values.
- Verify `/health/live` returns `200`.
- Verify `/health/ready` returns `200` or an intentional `degraded` state that you accept.
- Confirm trusted hosts and allowed origins match the real deployment domains.
- Confirm rate-limit values fit expected traffic.

## Frontend

- Copy `src/frontend/.env.example` to `src/frontend/.env` if you need environment-specific values.
- Run `npm install`.
- Run `npm run lint`.
- Run `npm run build`.
- Confirm the dashboard shows the expected readiness state and WebSocket connection.

## Verification

- Run `python -m pytest src/api/tests/test_app_smoke.py src/api/tests/test_end_to_end.py tests/test_transaction_scoring.py`
- Run `ruff check src tests`
- Smoke-test one transaction request, one NLP request, one readiness request, and one WebSocket ping.

## Deployment

- Build `Dockerfile.api`.
- Build `Dockerfile.frontend`.
- Start `docker-compose.yml`.
- Verify the frontend can reach the backend through `/api` and `/ws`.

## Operations

- Confirm logs are collected from the API container.
- Confirm restart policy is enabled.
- Confirm model artifacts and datasets required for the chosen features are mounted or baked into the image.
- Confirm secrets are stored outside the repository.
