from __future__ import absolute_import

import os
from dotenv import read_dotenv

from celery import Celery

read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
# set the default Django settings module for the 'celery' program.
environment = os.environ.get("POSTBOX_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "postbox.settings.{}".format(environment))

from django.conf import settings  # noqa

app = Celery('postbox')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
