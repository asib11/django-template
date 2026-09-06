# Template

A Django REST API project template with JWT authentication, user management, and Docker support.

## Features

- Django 5.x.x with Django REST Framework
- JWT Authentication using SimpleJWT
- PostgreSQL database support (with SQLite fallback)
- API documentation with drf-yasg (Swagger/OpenAPI)
- CORS headers configuration
- Docker support
- User management system
- Custom permissions and serializers

## Prerequisites

- Python 3.10+
- PostgreSQL (optional, SQLite is used by default)
- pip (Python package manager)
- Virtual environment (recommended)

## Quick Setup

### Option 1: Using the Setup Script

The fastest way to get started:

```bash
# Make the script executable
chmod +x entrypoint.sh

# Run the setup script
./entrypoint.sh
```

This script will:
- Create a virtual environment
- Activate it
- Copy `.env.sample` to `.env` (if available)
- Install all dependencies
- Run migrations

### Option 2: Manual Setup

1. **Clone the repository**
```bash
git clone <repository-url>
```

2. **Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root with the following variables:

```env
# Debug mode (True for development, False for production)
DEBUG=True

# Django secret key (generate a secure key for production)
SECRET_KEY=your-secret-key-here

# Database URL (optional, defaults to SQLite)
# For PostgreSQL: postgresql://user:password@localhost:5432/dbname
DATABASE_URL=sqlite:///db.sqlite3

# CORS settings (comma-separated URLs)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Project configuration (optional)
PROJECT_NAME=Django Project
PROJECT_DESCRIPTION=Django REST API Project
PROJECT_VERSION=v1
SWAGGER_DEFAULT_API_URL=http://127.0.0.1:8000

# Production settings (optional)
PROD_ENV_DISABLE_SWAGGER=False
PROD_ENV_DISABLE_ADMIN=False
```

5. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create a superuser (optional)**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## Docker Setup

### Using Docker

1. **Build the Docker image**
```bash
docker build -t django-template .
```

2. **Run the container**
```bash
docker run -p 8000:8000 -v $(pwd):/app django-template
```

### Using Docker Compose (if available)

```bash
docker-compose up
```

## Running Tests

This project uses Django's built-in test runner (works with any app in this codebase — swap
`<app_name>` / `<app_name>.tests.<ClassName>` / `...::test_method_name` for the app or test you want).

### Prerequisites

Make sure migrations exist for every app before running tests, otherwise Django's test
database won't have the required tables:

```bash
python manage.py makemigrations
```

### Basic Commands

Run the entire test suite (all apps):

```bash
python manage.py test
```

Run tests for a single app:

```bash
python manage.py test <app_name>
```

Run a single test class:

```bash
python manage.py test <app_name>.tests.<TestClassName>
```

Run a single test method:

```bash
python manage.py test <app_name>.tests.<TestClassName>.<test_method_name>
```

### Verbosity

Control how much detail is printed while tests run:

```bash
python manage.py test <app_name> -v 0   # Silent — only final OK/FAILED
python manage.py test <app_name> -v 1   # Default — dot progress (. per passing test)
python manage.py test <app_name> -v 2   # Verbose — prints each test's name and result
python manage.py test <app_name> -v 3   # Very verbose — includes DB setup/teardown logs
```

Use `-v 2` when writing new tests or debugging a failure — it shows exactly which test
ran and whether it passed.

### Speeding Up Repeated Runs

By default, Django creates a fresh test database, applies all migrations, runs the
tests, then destroys the database — every single run. On larger projects this migration
step can be slow.

Use `--keepdb` to reuse the test database between runs (only new migrations get applied):

```bash
python manage.py test <app_name> --keepdb
```

> If you change model fields significantly, run once **without** `--keepdb` to avoid
> schema drift between the kept test database and your current models.

### Running in Parallel (optional, for large suites)

```bash
python manage.py test --parallel
```

### Combining Flags

```bash
python manage.py test <app_name> -v 2 --keepdb
```

### Using pytest instead (if `pytest-django` is installed)

```bash
pytest <app_name>/tests.py -v
pytest <app_name>/tests.py::<TestClassName>::<test_method_name> -v
pytest --reuse-db          # equivalent of --keepdb
```

### Mocking External Services

When a test touches an external API (payment gateway, AI/LLM calls, email sending,
PDF/file generation libraries, etc.), mock it instead of calling the real service —
tests should be fast, deterministic, and runnable offline/in CI without real credentials:

```python
from unittest.mock import patch

@patch('<app_name>.<module>.<external_call_function>')
def test_something(self, mock_external_call):
    mock_external_call.return_value = {"example": "response"}
    # ... call the view/endpoint under test and assert on the result
```

### Isolating Uploaded/Generated Files

If tests create files (uploads, generated PDFs, images), point `MEDIA_ROOT` at a temp
directory so test runs don't pollute the real `media/` folder, and clean it up after:

```python
import shutil
import tempfile
from django.test import override_settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class MyTestCase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
```

### Quick Checklist Before Pushing

- [ ] `python manage.py makemigrations --check` — no missing migrations
- [ ] `python manage.py test` — full suite passes
- [ ] New endpoints/permissions have at least: an "unauthorized/forbidden" case, a
      "happy path" case, and one "not found / bad input" case

## API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`

## Project Structure

```
.
├── common/              # Common models, serializers, and utilities
├── helpers/             # Helper functions and utilities
├── projectile/          # Main project configuration
├── user/               # User management app
├── cache/              # Cache directory
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── entrypoint.sh       # Docker entrypoint script
└── pytest.ini          # Pytest configuration
```

## Development

### Collecting Static Files

```bash
python manage.py collectstatic
```

### Creating New Apps

```bash
python manage.py startapp <app_name>
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env` file
2. Generate a strong `SECRET_KEY`
3. Configure a PostgreSQL database
4. Set appropriate `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`
5. Use a production-grade server like Gunicorn:

```bash
gunicorn projectile.wsgi --access-logfile - -w 4 -b 0.0.0.0:8000
```

## License

See the `LICENSE` file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
