from __future__ import absolute_import
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import Box, Message

from celery import shared_task


@shared_task
def process_email(message_id, form_data):
    message = Message.objects.get(id=message_id)
    box = message.box
    subject = "New submission to your box: {}".format(box)
    # TODO SignMessage Here
    email = EmailMultiAlternatives(subject, form_data["message"],
                                   settings.DEFAULT_FROM_EMAIL,
                                   [box.owner.email])
    email.send()
    now = timezone.now()
    box.last_sent_at = now
    box.save()
    message.sent_at = now
    message.status = Message.SENT
    message.save()
