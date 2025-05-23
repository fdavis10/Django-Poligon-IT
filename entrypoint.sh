#!/bin/bash

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Start migrations..."
    python backend/manage.py migrate --noinput
    echo "Migrations is succesfull..."

    echo "Collect static files..."
    python backend/manage.py collectstatic --noinput
    echo "Static files is collected..."

    echo "Start Gunicorn..."
    exec gunicorn backend.poligon_it.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 300 \
    --log-level debug
    echo "Gunicorn started is succesfull..."
fi

exec "$@"
