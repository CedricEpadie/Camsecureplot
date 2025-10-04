#!/bin/bash
set -e  

echo "🚀 Lancement de Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT &

echo "⚡ Lancement de Celery worker..."
celery -A config worker -l info
