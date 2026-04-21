#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${PROJECT_ROOT}/.venv"
FRONTEND_DIR="${PROJECT_ROOT}/src/frontend"
PIDS=()

cleanup() {
  if [[ "${#PIDS[@]}" -gt 0 ]]; then
    echo
    echo "Stopping services..."
    for pid in "${PIDS[@]}"; do
      if kill -0 "${pid}" >/dev/null 2>&1; then
        kill "${pid}" >/dev/null 2>&1 || true
      fi
    done
    wait || true
  fi
}

trap cleanup EXIT INT TERM

if [[ ! -d "${VENV_PATH}" ]]; then
  echo "Missing virtual environment at ${VENV_PATH}"
  echo "Run:"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
  echo "  python -m spacy download en_core_web_sm"
  exit 1
fi

if [[ ! -d "${FRONTEND_DIR}/node_modules" ]]; then
  echo "Missing frontend dependencies in ${FRONTEND_DIR}/node_modules"
  echo "Run:"
  echo "  cd src/frontend && npm install"
  exit 1
fi

source "${VENV_PATH}/bin/activate"

echo "Starting FastAPI on http://localhost:8000"
(cd "${PROJECT_ROOT}" && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000) &
PIDS+=("$!")

echo "Starting React frontend on http://localhost:5173"
(cd "${FRONTEND_DIR}" && npm run dev -- --host 0.0.0.0 --port 5173) &
PIDS+=("$!")

echo "Starting Streamlit on http://localhost:8501"
(cd "${PROJECT_ROOT}" && streamlit run App_Frontend.py) &
PIDS+=("$!")

echo
echo "Services are starting:"
echo "  React:     http://localhost:5173"
echo "  FastAPI:   http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
echo "  Streamlit: http://localhost:8501"
echo
echo "Press Ctrl+C in this terminal to stop all services."

wait
