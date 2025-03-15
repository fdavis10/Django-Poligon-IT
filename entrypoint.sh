#!/bin/sh

# Останавливаем выполнение скрипта при ошибке
set -e

# Ожидаем, пока база данных не будет доступна
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database started"

# Применяем миграции
echo "Applying migrations..."
python /app/poligon_it/manage.py migrate

# Запускаем сервер
echo "Starting server..."
python /app/manage.py migrate django_celery_beat
exec "$@"
