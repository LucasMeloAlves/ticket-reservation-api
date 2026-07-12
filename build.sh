#!/usr/bin/env bash
# Render build script.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Seed demo data only if the database is empty (fresh deploy).
python manage.py seed_demo || true
