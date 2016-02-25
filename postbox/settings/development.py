from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "postbox_dev",
    }
}


# Development Applications
INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions'
)


