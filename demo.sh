#!/usr/bin/env bash
set -euo pipefail

# Demo script for local (SQLite) flow — safe and non-destructive
# Usage: ./demo.sh

echo "1) Activate virtualenv (or create it):"
if [ ! -d "venv" ]; then
  echo "- creating venv"
  python3 -m venv venv
fi
. venv/bin/activate

echo "2) Install requirements (if not installed):"
pip install -r requirements.txt

echo "3) Enable local sqlite flow"
export USE_SQLITE=true

echo "4) Apply migrations"
python manage.py migrate --noinput

echo "5) Ingest data synchronously"
python manage.py ingest_data --sync

echo "Demo finished: data ingested into db.sqlite3"
