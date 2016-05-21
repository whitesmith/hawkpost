from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "hawkpost_dev",
    }
}

# If the DB_HOST was specified it is overriding the default connection
if 'DB_HOST' in os.environ:
    DATABASES['default']['HOST'] = os.environ.get("DB_HOST")
    DATABASES['default']['PORT'] = os.environ.get("DB_PORT", 5432)
    DATABASES['default']['USER'] = os.environ.get("DB_USER")
    DATABASES['default']['NAME'] = os.environ.get("DB_NAME", "hawkpost_dev")

    if 'DB_PASSWORD' in os.environ:
        DATABASES['default']['PASSWORD'] = os.environ.get("DB_PASSWORD")

# Development Applications
INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions'
)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "127.0.0.1")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 1025)
