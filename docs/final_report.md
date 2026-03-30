# Final Report

## Introduction

This project explores a multimodal fraud detection system that combines
structured transaction features, anomaly detection, phishing-style text
analysis, and document-image fraud signals behind one API and monitoring
dashboard. I designed it as a practical product-shaped prototype rather than a
single notebook experiment, so the repository includes serving, monitoring,
tests, CI, and deployment assets alongside the model code.

The project goal is to show how different AI signals can support one fraud
workflow. A suspicious transaction may look abnormal because of its amount and
velocity, because its message resembles phishing, or because an uploaded
document appears manipulated. Bringing those perspectives together makes the
fraud story stronger than relying on one model alone.

## Technical Review

The backend is built with FastAPI and split into modular routers for
transactions, NLP, analytics, and CV. I used this structure so each modality
can evolve independently while still contributing to one service boundary. The
API also includes health and readiness endpoints, request timing headers,
security headers, and a WebSocket endpoint for live dashboard updates.

The frontend is a React dashboard that consumes shared API helpers and a live
WebSocket hook. I use it to present operator-facing information like readiness,
live transaction risk, and connection state. This makes the repository easier
to demo because the user can see both scoring and system health in one place.

The project also includes:

- CI for backend tests and frontend lint/build checks
- Dockerfiles and Compose orchestration for deployment
- readiness reporting for model artifacts and runtime dependencies
- issue-driven documentation for evaluation, ethics, and release work

## Design and Implementation

The implementation centers on a small number of clear product flows.

1. Transaction scoring:
   the API accepts a transaction payload, validates the supported feature
   profile, computes a transaction risk score, and returns a structured response
   with metadata and timestamp.

2. Live monitoring:
   the same transaction-scoring logic is reused by the WebSocket endpoint so
   the dashboard can receive live results without duplicate business logic.

3. Model readiness:
   the readiness service checks whether optional and required assets such as the
   NLP vectorizer, CV weights, anomaly model, and output directories are
   available before traffic is routed.

4. CV and NLP support:
   the repository includes preprocessing, training, and saved artifacts so the
   project can demonstrate multimodal expansion rather than a transaction-only
   system.

Key supporting files include:

- `src/api/main.py`
- `src/api/routers/transactions.py`
- `src/api/services/readiness.py`
- `src/train/train_anomaly_model.py`
- `src/train/evaluate_anomaly_model.py`
- `src/train/train_cv_model.py`
- `src/train/evaluate_cv_model.py`
- `src/frontend/src/App.jsx`

## Evaluation

The project now contains stronger technical evidence than a basic demo-only
submission. On the backend side, smoke tests cover the root, health, readiness,
rate limiting, and WebSocket ping routes. Integration tests compare low-risk
and high-risk transaction payloads and now also validate that a scored
transaction can be sent over the WebSocket path and returned with the expected
response shape and low latency.

For the model paths:

- the anomaly model now has one consistent artifact path for training, loading,
  readiness checks, and evaluation
- anomaly evaluation compares the anomaly detector with a supervised baseline to
  estimate how many fraud cases anomaly detection catches that the classifier
  misses, and how many extra false positives it introduces
- the CV evaluation helper now reports accuracy, precision, recall, and
  confusion counts instead of only one top-line number
- the evaluation notebook provides a concrete location for producing plots and
  charts for the final submission

Frontend quality also improved because linting and production build verification
 were added to the workflow. This matters because the dashboard is part of the
project deliverable, not a side demo.

## Ethics and Social Impact

I treat this system as a decision-support tool, not a final automated fraud
judge. Fraud datasets can reflect sampling bias, synthetic distortions are not
the same as real-world forgery, and false positives can unfairly affect
legitimate users. For those reasons, the safest project framing is that a high
risk score should trigger review, additional checks, or stepped-up
authentication rather than an irreversible denial.

This project also raises transparency questions. If multiple model signals are
combined, operators need some understanding of what contributed to the result.
That is why the API returns structured detail fields and the repository
includes documentation that explains how each model supports the overall fraud
workflow.

## Project Management and Future Work

The repository is organized around GitHub issues and now includes clearer
artifacts for model evaluation, ethics, integration validation, slide content,
and report content. That structure supports traceability because each technical
improvement can be connected back to a planned task.

The next priorities I would recommend are:

- finish browser-level end-to-end validation of dashboard live updates
- capture final screenshots for the report and presentation
- deepen the evaluation notebook with executed plots and saved figures
- continue reducing prototype-style duplication in older training paths
- tighten runtime dependencies for smaller production containers

## GitHub Evidence

The final submission should include screenshots of:

- the GitHub issue board or issue list
- recent commits showing production hardening and evaluation work
- the CI workflow file and a successful Actions run

I left this report in Markdown so those screenshots can be added cleanly before
submission without rewriting the rest of the document.

## AI Transparency Statement

I used AI coding assistance to review repository state, improve code quality,
unify inconsistent training and inference paths, strengthen tests, and draft
project documentation. I did not treat AI output as automatically correct. I
checked the local repository, verified files and datasets directly, and only
marked issue work complete when the codebase contained supporting evidence.
