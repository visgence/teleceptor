#!/bin/bash
source venv/bin/activate
if [[ -v PROD && "$PROD" == "true" ]]; then
    echo "Running in production mode"
    python manage.py collectstatic --noinput
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser --noinput
    python -m gunicorn teleceptor.wsgi:application --bind 0.0.0.0:$DJANGO_PORT --workers 4
else
    echo "Running in development mode"
    python manage.py makemigrations
    python manage.py migrate
    $@ 
fi