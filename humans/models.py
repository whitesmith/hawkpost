from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from timezone_field import TimeZoneField


class User(AbstractUser):
    """
        Project's base user model
    """
    organization = models.CharField(null=True, blank=True, max_length=80)
    public_key = models.TextField(blank=True, null=True)
    fingerprint = models.CharField(null=True, blank=True, max_length=50)
    keyserver_url = models.URLField(null=True, blank=True)
    server_signed = models.BooleanField(default=False)

    timezone = TimeZoneField(default='UTC')

    def has_setup_complete(self):
        if self.public_key and self.fingerprint:
            return True
        return False

    @property
    def has_public_key(self):
        return True if self.public_key else False

    @property
    def has_keyserver_url(self):
        return True if self.keyserver_url else False


class Notification(models.Model):
    """
        These notifications are emails sent to all users (or some subset)
        by an Administrator. Just once.
    """

    subject = models.CharField(null=False, blank=False, max_length=150)
    body = models.TextField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    sent_at = models.DateTimeField(null=True)
    send_to = models.ForeignKey(Group, null=True, blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.subject

    def delete(self):
        return super().delete() if not self.sent_at else False
