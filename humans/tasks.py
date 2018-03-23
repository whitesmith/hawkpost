from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
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
        raise ValueError(_('The Url provided does not contain a public key'))


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
    logger.info(_('Start updating user keys'))
    for user in users:
        logger.info(_('Working on user: {}').format(user.email))
        logger.info(_('URL: {}').format(user.keyserver_url))
        try:
            key = fetch_key(user.keyserver_url)
        except:
            logger.error(_('Unable to fetch new key'))
            continue

        # Check key
        fingerprint, *state = key_state(key)

        if state[0] in ["expired", "revoked"]:
            # Email user and disable/remove key
            send_email(user, _('Hawkpost: {} key').format(state[0]),
                       "humans/emails/key_{}.txt".format(state[0]))
            user.fingerprint = ""
            user.public_key = ""
            user.keyserver_url = ""
            user.save()
        elif state[0] == "invalid":
            # Alert the user and remove keyserver_url
            send_email(user,
                       _('Hawkpost: Keyserver Url providing an invalid key'),
                       "humans/emails/key_invalid.txt")
            user.keyserver_url = ""
            user.save()
        elif fingerprint != user.fingerprint:
            # Email user and remove the keyserver url
            send_email(user, _('Hawkpost: Fingerprint mismatch'),
                       "humans/emails/fingerprint_changed.txt")
            user.keyserver_url = ""
            user.save()
        elif state[0] == "valid":
            user.public_key = key
            user.save()

    logger.info(_('Finished Updating user keys'))

# Every day at 5h30 AM UTC
@periodic_task(run_every=(crontab(minute=30, hour=5)), ignore_result=True)
def validate_public_keys():
    users = User.objects.exclude(
        Q(public_key__isnull=True) | Q(public_key__exact=''))
    logger.info(_('Start validating user keys'))
    for user in users:
        logger.info(_('Working on user: {}').format(user.email))
        key = user.public_key
        # Check key
        fingerprint, *state = key_state(key)

        if state[0] == "expired":
            # Email user and disable/remove key
            send_email(user, _('Hawkpost: {} key').format(state[0]),
                       "humans/emails/key_{}.txt".format(state[0]))
            user.fingerprint = ""
            user.public_key = ""
            user.save()

        elif state[0] == "valid":
            # Checks if key is about to expire
            days_to_expire = state[1]
            if days_to_expire == 7 or days_to_expire == 1:
                # Warns user if key about to expire
                send_email(user,
                           _('Hawkpost: Key will expire in {} day(s)').format(days_to_expire),
                           "humans/emails/key_will_expire.txt")


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
