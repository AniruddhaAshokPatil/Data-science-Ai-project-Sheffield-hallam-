# Integration Validation

I use this file to capture the strongest end-to-end evidence that currently
exists in the repository.

## Automated Checks

- backend smoke tests cover root, health, readiness, WebSocket ping, and rate limiting
- transaction integration tests compare low-risk and high-risk payloads
- WebSocket integration now sends a scored transaction payload through
  `/ws/transactions` and confirms the broadcast response shape and latency
- frontend lint and production build both pass locally

## What the Current End-to-End Path Covers

1. a transaction payload reaches the backend
2. the backend validates and scores it
3. the same scoring logic can be triggered over WebSocket
4. the frontend can request readiness and transaction scoring from shared API helpers
5. the dashboard can listen for live updates over WebSocket

## What Still Needs Manual Proof

- browser-level confirmation that the dashboard updates live while connected
- a fully recorded demo of backend, WebSocket, and frontend running together
- final latency screenshots or logs captured for the report/presentation

## Why This Still Matters

Even with those remaining manual checks, the repo now contains enough automated
coverage to prove that the core backend event flow is not just a mockup. The
tests exercise the same HTTP and WebSocket entry points that the project demo
depends on.
