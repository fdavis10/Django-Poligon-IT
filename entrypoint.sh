#!/bin/sh


set -e


echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database started"


echo "Applying migrations..."
python /app/poligon_it/manage.py makemigrations
python /app/poligon_it/manage.py migrate
python /app/poligon_it/manage.py migrate django_celery_beat

echo "Starting server..."
exec "$@"
