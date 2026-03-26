#!/usr/bin/env bash
set -e

# Run from the project root
# 1) Activate your venv (optional but recommended)
# source .venv/bin/activate

# 2) Install deps
python3 -m pip install --upgrade pip
python3 -m pip install -r src/api/requirements.txt

# 3) Start API from the project root
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

chmod +x src/api/start.sh
