#!/bin/sh
set -e

ATTEMPTS=0
MAX_ATTEMPTS=15

until python manage.py migrate --noinput; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "Database not reachable after $MAX_ATTEMPTS attempts, aborting" >&2
    exit 1
  fi
  echo "Database not ready yet, retrying in 3s... ($ATTEMPTS/$MAX_ATTEMPTS)"
  sleep 3
done

python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 60
