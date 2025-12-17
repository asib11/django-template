#!/usr/bin/env bash

mkdir -p staticfiles
python manage.py collectstatic --no-input

python manage.py migrate
# python manage.py runserver 0.0.0.0:8000

gunicorn projectile.wsgi \
    --access-logfile - \
    -w 4 \
    -b 0.0.0.0:8000

