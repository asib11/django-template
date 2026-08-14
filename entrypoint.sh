#!/usr/bin/env bash
set -e

ENV_FOLDER=".venv"
ENV_FILE=".env"

if [ ! -d "$ENV_FOLDER" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $ENV_FOLDER
    source $ENV_FOLDER/bin/activate
    pip install pip wheel setuptools -U
    pip install -r requirements.txt
else
    source $ENV_FOLDER/bin/activate
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Copying .env.example to .env ..."
    cp .env.example .env
fi

# Wait for PostgreSQL to be ready
echo "Waiting for database to be ready..."
python3 - <<'PY'
import os, sys, time

db_url = os.environ.get("DATABASE_URL", "")
if not db_url:
    print("WARNING: DATABASE_URL is not set, skipping DB wait.")
    sys.exit(0)

try:
    import dj_database_url
    import psycopg2
    config = dj_database_url.parse(db_url)
    for attempt in range(1, 31):
        try:
            conn = psycopg2.connect(
                host=config["HOST"],
                port=config.get("PORT") or 5432,
                user=config["USER"],
                password=config["PASSWORD"],
                dbname=config["NAME"],
                connect_timeout=3,
            )
            conn.close()
            print(f"Database is ready (attempt {attempt}).")
            sys.exit(0)
        except Exception as e:
            print(f"Attempt {attempt}/30 — DB not ready: {e}")
            time.sleep(2)
    print("ERROR: Database did not become ready in time.")
    sys.exit(1)
except ImportError:
    print("psycopg2/dj_database_url not available, skipping DB wait.")
PY

# Bootstrap missing migrations directories for any app that lacks one
echo "Bootstrapping missing migrations packages..."
python3 - <<'PY'
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectile.settings")
django.setup()

from django.apps import apps

for app_config in apps.get_app_configs():
    if app_config.name.startswith("django."):
        continue
    migrations_dir = os.path.join(app_config.path, "migrations")
    if not os.path.isdir(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)
        init_file = os.path.join(migrations_dir, "__init__.py")
        open(init_file, "a").close()
        print(f"Created migrations package: {migrations_dir}")

print("Migration packages check complete.")
PY

echo "Running makemigrations..."
python3 manage.py makemigrations

echo "Collecting static files..."
python3 manage.py collectstatic --no-input

echo "Running migrate..."
python3 manage.py migrate

echo "Starting Celery worker..."
mkdir -p tmp
celery -A projectile worker \
    --loglevel=info \
    --concurrency=4 \
    --logfile=tmp/celery-worker.log &

echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 projectile.asgi:application
