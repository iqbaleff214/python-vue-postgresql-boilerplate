#!/bin/sh
set -e

# Run migrations only for the main backend service (not celery worker)
if [ "$1" = "uvicorn" ]; then
    echo "Running database migrations..."
    alembic upgrade head
    echo "Running database seeder..."
    python seed.py
fi

exec "$@"
