#!/bin/sh
set -e
python manage.py migrate --noinput
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 toxic_project.wsgi:application
