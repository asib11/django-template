import os
import environ
from dotenv import load_dotenv
from helpers.env import is_enabled
from helpers.env import get_items


load_dotenv()


BASE_DIR = os.path.abspath('.')


env = environ.Env(
    DEBUG=(bool, False),
    DATABASE_URL=(str, f'sqlite:///{BASE_DIR}/db.sqlite3'),
)




DEV_TEST_SHOW_ALL_REGISTERED_MODELS = is_enabled('DEV_TEST_SHOW_ALL_REGISTERED_MODELS')
DEV_TEST_MULTIPARTPARSER_ONLY = is_enabled('DEV_TEST_MULTIPARTPARSER_ONLY')
SWAGGER_DEFAULT_API_URL = os.getenv('SWAGGER_DEFAULT_API_URL') or 'http://127.0.0.1:8000'
PROJECT_NAME = os.getenv('PROJECT_NAME') or 'Django Project'
PROJECT_DESCRIPTION = os.getenv('PROJECT_DESCRIPTION') or PROJECT_NAME
PROJECT_VERSION = os.getenv('PROJECT_VERSION') or 'v1'


DEBUG = is_enabled('DEBUG')
SECRET_KEY = os.getenv('SECRET_KEY')
DB = env.db('DATABASE_URL')
PROD_ENV_DISABLE_SWAGGER = is_enabled('PROD_ENV_DISABLE_SWAGGER')
PROD_ENV_DISABLE_ADMIN = is_enabled('PROD_ENV_DISABLE_ADMIN')


CORS_ALLOWED_ORIGINS = get_items('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS


EMAIL_HOST = os.getenv('EMAIL_HOST') or 'smtp.gmail.com'
EMAIL_PORT = os.getenv('EMAIL_PORT') or 587
EMAIL_USE_TLS = is_enabled('EMAIL_USE_TLS')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
