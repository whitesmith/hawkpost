from __future__ import absolute_import
from dotenv import read_dotenv
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal
from celery import Celery as BaseCelery
import os

read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
# set the default Django settings module for the 'celery' program.
environment = os.environ.get("HAWKPOST_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "hawkpost.settings.{}".format(environment))

from django.conf import settings  # noqa


class Celery(BaseCelery):
    def on_configure(self):
        client = Client(settings.RAVEN_CONFIG["dsn"])
        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)
        # hook into the Celery error handler
        register_signal(client)


if environment == "development":
    app = BaseCelery('hawkpost')
else:
    app = Celery('hawkpost')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
