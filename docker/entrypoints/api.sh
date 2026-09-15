#!/usr/bin/env bash
set -euo pipefail

cd /app/apps/api

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
