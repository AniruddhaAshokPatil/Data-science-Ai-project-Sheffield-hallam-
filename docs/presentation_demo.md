# Presentation and Demo Runbook

I use this file as the live-demo companion to `docs/presentation_slides.md` so
the team has both the slide content and a practical run order.

## Slide Deck

- Slide deck content now lives in `docs/presentation_slides.md`
- This runbook focuses on speaking order, live steps, and fallback options

## Demo Script

### Step 1: Show the API is alive
- Open `/health`
- Open `/health/ready`

### Step 2: Show the dashboard
- Open the frontend dashboard
- Point out readiness state and WebSocket status

### Step 3: Trigger a transaction score
- Submit a high-risk transaction from the controls panel
- Show the risk result appearing in the live table
- Mention that the same scoring path is covered by integration tests

### Step 4: Explain multimodal expansion
- Mention NLP and CV routes
- Mention how readiness reports degraded components

## Rehearsal Notes

- One person should handle the architecture explanation.
- One person should drive the live demo.
- One person should cover ethics and limitations.
- One person should answer project management and GitHub workflow questions.
- One person should keep the backup terminal commands ready in case the UI needs a refresh.

## Backup Demo Path

- If the dashboard stalls, show `/docs` and submit the transaction route directly
- If WebSocket updates do not appear, show the passing WebSocket integration test
- If a model is unavailable, use `/health/ready` to explain degraded readiness honestly

## Remaining Manual Work

- rehearse speaking order as a team
- capture final screenshots for the deck and report
- record who presents each slide during the final submission slot
