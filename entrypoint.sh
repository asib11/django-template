#!/usr/bin/env bash


ENV_FOLDER=".venv"
ENV_FILE=".env"

if [ ! -d "$ENV_FOLDER" ]; then
    python3 -m venv $ENV_FOLDER
    source $ENV_FOLDER/bin/activate
    pip install pip wheel setuptools -U
    pip install -r requirements.txt
else
    source $ENV_FOLDER/bin/activate
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Copy .env.example to .env and configure it before running the application."
    cp .env.example .env
fi

# mkdir -p staticfiles
python3 manage.py collectstatic --no-input

python3 manage.py migrate

celery -A projectile worker --loglevel=info --concurrency=4 --logfile=tmp/celery-worker.log &

python3 manage.py runserver 0.0.0.0:8000

# gunicorn projectile.wsgi \
#     --access-logfile - \
#     -w 4 \
#     -b 0.0.0.0:8000

# daphne -u /tmp/daphne.sock projectile.asgi:application
# daphne -b 0.0.0.0 -p 8000 projectile.asgi:application
