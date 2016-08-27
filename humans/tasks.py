from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from .models import User, Notification
from .utils import key_state
import requests

logger = get_task_logger(__name__)


def fetch_key(url):
    res = requests.get(url)
    begin = res.text.find("-----BEGIN PGP PUBLIC KEY BLOCK-----")
    end = res.text.find("-----END PGP PUBLIC KEY BLOCK-----")
    if 200 <= res.status_code < 300 and begin >= 0 and end > begin:
        return res.text[begin:end + 34]
    else:
        raise ValueError("The Url provided does not contain a public key")


def send_email(user, subject, template):
    content = render_to_string(template, context={"user": user})
    email = EmailMultiAlternatives(subject, content,
                                   settings.DEFAULT_FROM_EMAIL,
                                   [user.email])
    email.send()


# Every day at 4 AM UTC
@periodic_task(run_every=(crontab(minute=0, hour=4)), ignore_result=True)
def update_public_keys():
    users = User.objects.exclude(
        Q(keyserver_url__isnull=True) | Q(keyserver_url__exact=''))
    logger.info("Start updating user keys")
    for user in users:
        logger.info("Working on user: {}".format(user.email))
        logger.info("URL: {}".format(user.keyserver_url))
        try:
            key = fetch_key(user.keyserver_url)
        except:
            logger.error("Unable to fetch new key")
            continue

        # Check key
        fingerprint, state = key_state(key)

        if state in ["expired", "revoked"]:
            # Email user and disable/remove key
            send_email(user, "Hawkpost: {} key".format(state),
                       "humans/emails/key_{}.txt".format(state))
            user.fingerprint = ""
            user.public_key = ""
            user.keyserver_url = ""
            user.save()
        elif state == "invalid":
            # Alert the user and remove keyserver_url
            send_email(user,
                       "Hawkpost: Keyserver Url providing an invalid key",
                       "humans/emails/key_invalid.txt")
            user.keyserver_url = ""
            user.save()
        elif fingerprint != user.fingerprint:
            # Email user and remove the keyserver url
            send_email(user, "Hawkpost: Fingerprint mismatch",
                       "humans/emails/fingerprint_changed.txt")
            user.keyserver_url = ""
            user.save()
        elif state == "valid":
            # Update the key store in the database
            user.public_key = key
            user.save()

    logger.info("Finished Updating user keys")


@shared_task
def send_email_notification(subject, body, email):
    email = EmailMultiAlternatives(subject, body,
                                   settings.DEFAULT_FROM_EMAIL,
                                   [email])
    email.send()


@shared_task
def enqueue_email_notifications(notification_id, group_id):
    notification = Notification.objects.get(id=notification_id)
    if group_id:
        users = User.objects.filter(groups__id=group_id)
    else:
        users = User.objects.all()

    for user in users:
        send_email_notification.delay(notification.subject,
                                      notification.body,
                                      user.email)
