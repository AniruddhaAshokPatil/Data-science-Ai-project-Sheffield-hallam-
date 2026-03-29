# Fraud Detection Command Dashboard

A React dashboard that talks to the FastAPI backend and surfaces readiness,
live transactions, and operator actions in one place.

## Prerequisites

- Node.js 18+ installed
- Your backend running at `http://127.0.0.1:8000`
  Start it from the project root:

```bash
uvicorn src.api.main:app --reload
```

## Quick Start

```bash
cd src/frontend
npm install
npm run dev
```

## Production Build

```bash
cd src/frontend
cp .env.example .env
npm install
npm run lint
npm run build
```

I use `/api` and `/ws` by default so the dashboard can sit behind the same
public host as the backend when deployed through Nginx or another proxy.
