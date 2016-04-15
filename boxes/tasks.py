from __future__ import absolute_import
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import Box

from celery import shared_task


@shared_task
def process_email(box_id, form_data):
    box = Box.objects.get(id=box_id)
    subject = "New submission to your box: {}".format(box)
    # TODO SignMessage Here
    email = EmailMultiAlternatives(subject, form_data["message"],
                                   settings.DEFAULT_FROM_EMAIL,
                                   [box.owner.email])
    email.send()
    box.last_sent_at = timezone.now()
    box.status = Box.SENT
    box.save()
