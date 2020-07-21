from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
import uuid


class Box(models.Model):

    OPEN = 10
    EXPIRED = 20
    DONE = 30
    CLOSED = 40

    STATUSES = (
        (OPEN, _('Open')),
        (EXPIRED, _('Expired')),
        (DONE, _('Done')),
        (CLOSED, _('Closed'))
    )

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True,
                                   verbose_name=_('Description'))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                            verbose_name=_('Unique ID'))

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='own_boxes',
                              verbose_name=_('Owner'))

    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='boxes',
                                        through='Membership',
                                        through_fields=('box', 'user'),
                                        verbose_name=_('Recipients'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))
    expires_at = models.DateTimeField(null=True, blank=True,
                                      verbose_name=_('Expires at'))

    status = models.IntegerField(choices=STATUSES, default=OPEN,
                                 verbose_name=_('Status'))
    max_messages = models.PositiveIntegerField(default=1, validators=[
                                               MinValueValidator(1)],
                                               verbose_name=_('Max. messages'))

    last_sent_at = models.DateTimeField(null=True,
                                        verbose_name=_('Last sent at'))

    class Meta:
        verbose_name = _('Box')
        verbose_name_plural = _('Boxes')

    def __str__(self):
        return self.name

    @staticmethod
    def get_status(name):
        return {
            "Open": Box.OPEN,
            "Expired": Box.EXPIRED,
            "Done": Box.DONE,
            "Closed": Box.CLOSED
        }.get(name, Box.OPEN)


class Membership(models.Model):

    KNOWLEDGE = 10
    NOTIFICATION = 20
    FULL = 30

    LEVELS = (
        (KNOWLEDGE, _('Knowledge of existence')),
        (NOTIFICATION, _('Activity notifications')),
        (FULL, _('Full access to content')),
    )

    access = models.IntegerField(choices=LEVELS, default=FULL,
                                 verbose_name=_('Rights'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))
    box = models.ForeignKey("Box", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')

    def __str__(self):
        return "{}.{}".format(self.id, self.get_access_display())


class Message(models.Model):

    ONQUEUE = 10
    SENT = 20
    FAILED = 30

    STATUSES = (
        (ONQUEUE, _('OnQueue')),
        (SENT, _('Sent')),
        (FAILED, _('Failed'))
    )

    box = models.ForeignKey(
        "Box", on_delete=models.CASCADE, related_name='messages')
    status = models.IntegerField(choices=STATUSES, default=ONQUEUE,
                                 verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))
    sent_at = models.DateTimeField(null=True, blank=True,
                                   verbose_name=_('Sent at'))
