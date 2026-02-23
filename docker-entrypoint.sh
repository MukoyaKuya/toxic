#!/bin/sh
set -e

# Optional migrations to avoid slowing cold starts in production.
# Set RUN_MIGRATIONS=true in the environment when you explicitly want
# this container start to run Django migrations.
if [ "$RUN_MIGRATIONS" = "true" ]; then
  python manage.py migrate --noinput
fi

# Single worker starts faster; Cloud Run handles horizontal scaling.
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 120 toxic_project.wsgi:application
