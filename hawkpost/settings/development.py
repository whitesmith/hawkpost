from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(',')

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
    'django_extensions',
)

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

INTERNAL_IPS = ['127.0.0.1']
if 'INTERNAL_IPS' in os.environ:
    INTERNAL_IPS += os.environ.get("INTERNAL_IPS").split(',')
