from .common import *
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [SITE_DOMAIN]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT"),
    }
}


# Installed Apps
# Development Applications
INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)


# Email Settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True


# Security Setings
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 600000
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_HTTPONLY = True


# Allauth Config
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# We trust that the chosen providers did the verification
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"


# Sentry Configuration
RAVEN_CONFIG = {
    'dsn': os.environ.get("SENTRY_URL")
}

# Axes Behind proxy
AXES_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]
