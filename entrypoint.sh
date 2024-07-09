#!/bin/bash

. /home/teleceptor/teleceptor/.env
cd /home/teleceptor/teleceptor/
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
# npm install --force
bash -c "gunicorn teleceptor.wsgi:application --bind 0.0.0.0:8000"
