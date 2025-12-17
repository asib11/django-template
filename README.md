# Django Template

A Django REST API project template with JWT authentication, user management, and Docker support.

## Features

- Django 4.2.18 with Django REST Framework
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
chmod +x initial.sh

# Run the setup script
./initial.sh
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
cd portavacation
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

This project uses pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest user/tests/
```

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
├── initial.sh          # Quick setup script
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
