#!/bin/bash
set -e
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput
$@