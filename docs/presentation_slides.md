# Fraud Detection Project Slides

## Slide 1: Title

Multimodal Fraud Detection Platform

- transaction scoring
- anomaly detection
- phishing-text analysis
- document-forgery checks

Speaker note:
I introduce the project as one joined-up fraud workflow rather than four
disconnected models.

## Slide 2: Problem

- fraud signals arrive in many forms
- a single model can miss context
- operators need live visibility, not only batch scoring

Speaker note:
I explain that real fraud operations care about behavior, language, and
documents at the same time.

## Slide 3: Solution

- FastAPI backend for unified scoring
- React dashboard for monitoring
- health/readiness endpoints for deployment visibility
- WebSocket updates for live events

Speaker note:
I show that the project is not just model training, but an end-to-end product
shape with serving and monitoring.

## Slide 4: System Architecture

- transaction route for structured features
- NLP route for suspicious text
- CV route for document images
- shared readiness service for model availability

Speaker note:
I walk through how the system supports modular growth while keeping one API
surface for the demo.

## Slide 5: Technical Highlights

- stricter input validation
- structured readiness report
- rate limiting and security headers
- CI, Docker packaging, and production-shaped frontend build

Speaker note:
I use this slide to show that the engineering work goes beyond notebook-only AI.

## Slide 6: Evaluation

- backend tests passing
- WebSocket scoring validated
- frontend lint/build passing
- evaluation scripts for anomaly and CV paths

Speaker note:
I keep this slide honest by distinguishing verified automation from remaining
manual demo checks.

## Slide 7: Ethics and Limitations

- dataset realism gaps
- possible bias and false positives
- system should support human review, not replace it

Speaker note:
I explain that fraud models can cause harm when over-trusted, so this project
frames AI as decision support.

## Slide 8: Demo Plan

- show `/health` and `/health/ready`
- open dashboard
- submit a risky transaction
- show live risk output

Speaker note:
I keep the demo simple so the audience sees a stable path, not too many moving parts.

## Slide 9: Future Work

- improve artifact-backed serving across all modalities
- deepen evaluation plots and calibration analysis
- finish full browser-level end-to-end evidence

Speaker note:
I end by showing this is a credible foundation with clear next steps.
