from __future__ import absolute_import
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

from .models import Message
from .email import GPGSignedEncryptedMessage

from celery import shared_task

@shared_task
def process_email(message_id, form_data):
    message = Message.objects.get(id=message_id)
    box = message.box
    msg = form_data["message"]
    subject = "New submission to your box: {}".format(box)

    if box.owner.server_signed:
        email = GPGSignedEncryptedMessage(subject, msg,
                                      settings.DEFAULT_FROM_EMAIL,
                                      [box.owner.email])
    else:
        email = EmailMultiAlternatives(subject, msg,
                                      settings.DEFAULT_FROM_EMAIL,
                                      [box.owner.email])

    # Output e-mail message for debug purposes
    # with open('email.mbox', 'w') as f:
    #     f.write(email.message().as_string(unixfrom=True))

    email.send()
    now = timezone.now()
    box.last_sent_at = now
    box.save()
    message.sent_at = now
    message.status = Message.SENT
    message.save()
