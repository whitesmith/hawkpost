from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid


class Box(models.Model):

    OPEN = 10
    EXPIRED = 20
    DONE = 30
    CLOSED = 40

    STATUSES = (
        (OPEN, 'Open'),
        (EXPIRED, 'Expired'),
        (DONE, 'Done'),
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
    expires_at = models.DateTimeField(null=True, blank=True)

    status = models.IntegerField(choices=STATUSES, default=OPEN)
    max_messages = models.PositiveIntegerField(default=1, validators=[
                                               MinValueValidator(1)])

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
            "Done": Box.DONE,
            "Closed": Box.CLOSED
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


class Message(models.Model):

    ONQUEUE = 10
    SENT = 20
    FAILED = 30

    STATUSES = (
        (ONQUEUE, 'OnQueue'),
        (SENT, "Sent"),
        (FAILED, "Failed")
    )

    box = models.ForeignKey("Box", related_name='messages')
    status = models.IntegerField(choices=STATUSES, default=ONQUEUE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
