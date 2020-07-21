from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField
from django.db import transaction


class User(AbstractUser):
    """
        Project's base user model
    """
    LANGUAGE_CHOICES = (
        ('en-us', 'English'),
        ('pt-pt', _('Portuguese')),
    )

    organization = models.CharField(
        null=True, blank=True, max_length=80, verbose_name=_('Organization'))
    public_key = models.TextField(
        blank=True, null=True, verbose_name=_('Public key'))
    fingerprint = models.CharField(
        null=True, blank=True, max_length=50, verbose_name=_('Fingerprint'))
    keyserver_url = models.URLField(
        null=True, blank=True, verbose_name=_('Key server URL'))
    timezone = TimeZoneField(default='UTC', verbose_name=_('Timezone'))
    language = models.CharField(
        default="en-us", max_length=16, choices=LANGUAGE_CHOICES, verbose_name=_('Language'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_fingerprint = self.fingerprint

    def save(self, *args, **kwargs):
        ip = kwargs.pop('ip', None)
        agent = kwargs.pop('agent', '')
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.base_fingerprint != self.fingerprint:
                self.keychanges.create(user=self,
                                       prev_fingerprint=self.base_fingerprint,
                                       to_fingerprint=self.fingerprint,
                                       ip_address=ip,
                                       agent=agent)
                self.base_fingerprint = self.fingerprint

    def has_setup_complete(self):
        if self.public_key and self.fingerprint:
            return True
        return False

    @property
    def has_github_login(self):
        return self.socialaccount_set.filter(provider='github').count() >= 1

    @property
    def has_public_key(self):
        return True if self.public_key else False

    @property
    def has_keyserver_url(self):
        return True if self.keyserver_url else False


class Notification(models.Model):
    """ These notifications are emails sent to all users (or some subset)
        by an Administrator. Just once.
    """

    subject = models.CharField(
        null=False, blank=False, max_length=150, verbose_name=_('Subject'))
    body = models.TextField(null=False, blank=False, verbose_name=_('Body'))

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('Updated at'))

    sent_at = models.DateTimeField(null=True, verbose_name=_('Sent at'))
    send_to = models.ForeignKey(
        Group, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Send to'))

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return self.subject

    def delete(self):
        return super().delete() if not self.sent_at else False


class KeyChangeRecord(models.Model):
    """ Records the information about the change of a key by the user.
        This allows the user to be aware of any suspicious activity
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='keychanges',
                             verbose_name=_('User'))
    prev_fingerprint = models.CharField(null=True,
                                        blank=True,
                                        max_length=50,
                                        verbose_name=_('Previous Fingerprint'))
    to_fingerprint = models.CharField(null=True,
                                      blank=True,
                                      max_length=50,
                                      verbose_name=_('To Fingerprint'))
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('KeyChangeRecord')
        verbose_name_plural = _('KeyChangeRecords')
