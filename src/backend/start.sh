#!/usr/bin/env bash
set -e

# Run from the project root
# 1) Activate your venv (optional but recommended)
# source .venv/bin/activate

# 2) Install deps
python3 -m pip install --upgrade pip
python3 -m pip install -r src/backend/requirements.txt

# 3) Start API (notice we run from src to make 'backend' a package)
cd src
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

chmod +x src/backend/start.sh

