#!/usr/bin/env bash


ENV_FOLDER=".venv"

if [ ! -d "$ENV_FOLDER" ]; then
    python -m venv $ENV_FOLDER
    . $ENV_FOLDER/bin/activate
    pip install pip wheel setuptools -U
    pip install -r requirements.txt
else
    . $ENV_FOLDER/bin/activate
fi



mkdir -p staticfiles
python manage.py collectstatic --no-input

python manage.py migrate

celery -A projectile worker --loglevel=info --concurrency=4 --logfile=tmp/celery-worker.log &

# python manage.py runserver 0.0.0.0:8000

# gunicorn projectile.wsgi \
#     --access-logfile - \
#     -w 4 \
#     -b 0.0.0.0:8000

# daphne -u /tmp/daphne.sock projectile.asgi:application
daphne -b 0.0.0.0 -p 8000 projectile.asgi:application