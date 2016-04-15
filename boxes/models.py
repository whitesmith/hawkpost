from django.db import models
from django.conf import settings
import uuid


class Box(models.Model):

    OPEN = 10
    EXPIRED = 20
    SENT = 30
    CLOSED = 40
    ONQUEUE = 50

    STATUSES = (
        (OPEN, 'Open'),
        (EXPIRED, 'Expired'),
        (SENT, 'Sent'),
        (ONQUEUE, 'On Queue'),
        (CLOSED, "Closed")
    )

    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='own_boxes')

    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='boxes',
                                        through='Membership',
                                        through_fields=('box', 'user'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    status = models.IntegerField(choices=STATUSES, default=OPEN)
    last_sent_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Box"
        verbose_name_plural = "Boxes"

    def __str__(self):
        return self.name

    @staticmethod
    def get_status(name):
        return {
            "Open": Box.OPEN,
            "Expired": Box.EXPIRED,
            "Sent": Box.SENT,
            "Closed": Box.CLOSED,
            "On Queue": Box.ONQUEUE
        }.get(name, Box.OPEN)


class Membership(models.Model):

    KNOWLEDGE = 10
    NOTIFICATION = 20
    FULL = 30

    LEVELS = (
        (KNOWLEDGE, 'Knowledge of existence'),
        (NOTIFICATION, 'Activity notifications'),
        (FULL, 'Full access to content'),
    )

    access = models.IntegerField(choices=LEVELS, default=FULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    box = models.ForeignKey("Box")
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"

    def __str__(self):
        return "{}.{}".format(self.id, self.get_access_display())
