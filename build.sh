#!/usr/bin/env bash
# build.sh — Render runs this during every deploy
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py init_admin
