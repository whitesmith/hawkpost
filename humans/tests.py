from django.contrib.auth.models import Group
from django.utils import timezone
from django.test import TestCase
from django.core import mail
from boxes.tests import create_and_login_user
from hawkpost import celery_app
from .models import Notification, User
from .forms import UpdateUserInfoForm
from .tasks import enqueue_email_notifications
from .utils import key_state
from .test_constants import VALID_KEY_FINGERPRINT, VALID_KEYSERVER_URL
from .test_constants import EXPIRED_KEY_FINGERPRINT
from .test_constants import REVOKED_KEY, EXPIRED_KEY, VALID_KEY

from copy import copy


def create_notification(sent=False, group=None):
    sent_at = timezone.now() if sent else None
    return Notification.objects.create(subject="Test subject",
                                       body="Test Body",
                                       sent_at=sent_at,
                                       send_to=group)


class UpdateUserFormTests(TestCase):

    def setUp(self):
        self.default_data = {
            "first_name": "some name",
            "last_name": "some last name",
            "company": "some company",
            "fingerprint": VALID_KEY_FINGERPRINT,
            "timezone": "UTC",
            "language": "en-us",
            "public_key": VALID_KEY,
            "old_password": "",
            "new_password1": "",
            "new_password2": "",
        }

    def test_empty_fingerprint(self):
        data = copy(self.default_data)
        data["fingerprint"] = ""
        form = UpdateUserInfoForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_fingerprint_plus_public_key(self):
        data = copy(self.default_data)
        data["fingerprint"] = VALID_KEY_FINGERPRINT
        data["public_key"] = VALID_KEY
        form = UpdateUserInfoForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_fingerprint_plus_keyserver_url(self):
        data = copy(self.default_data)
        data["keyserver_url"] = VALID_KEYSERVER_URL
        form = UpdateUserInfoForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_fingerprint_mismatch(self):
        data = copy(self.default_data)
        data["fingerprint"] = EXPIRED_KEY_FINGERPRINT
        form = UpdateUserInfoForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_empty_language(self):
        data = copy(self.default_data)
        data["language"] = ""
        form = UpdateUserInfoForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_non_valid_language(self):
        data = copy(self.default_data)
        data["language"] = "invalid"
        form = UpdateUserInfoForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_wrong_old_password(self):
        """
        Tests if the form is invalidated because the wrong password was sent
        """
        data = copy(self.default_data)
        data["old_password"] = "wrongpassword"
        user = create_and_login_user(self.client)
        form = UpdateUserInfoForm(data, instance=user)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue('old_password' in form.errors)

    def test_invalid_password(self):
        """
        Tests that Django password constraints are being tested
        """
        data = copy(self.default_data)
        data["old_password"] = '123123'
        data["new_password1"] = 'a'
        data["new_password2"] = 'a'
        user = create_and_login_user(self.client)
        user.set_password('123123')
        user.save()

        form = UpdateUserInfoForm(data, instance=user)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue('new_password2' in form.errors)

    def test_non_matching_passwords(self):
        """
        Tests if the form invalidates when password are valid but different
        """
        data = copy(self.default_data)
        data["old_password"] = '123123'
        data["new_password1"] = 'abcABCD123'
        data["new_password2"] = 'abcABCD1234'
        user = create_and_login_user(self.client)
        user.set_password('123123')
        user.save()

        form = UpdateUserInfoForm(data, instance=user)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue('new_password2' in form.errors)

class UtilsTests(TestCase):

    def test_invalid_key_state(self):
        fingerprint, state = key_state("invalid stuff")
        self.assertEqual(state, "invalid")

    def test_expired_key_state(self):
        fingerprint, state = key_state(EXPIRED_KEY)
        self.assertEqual(state, "expired")

    def test_revoked_key_state(self):
        fingerprint, state = key_state(REVOKED_KEY)
        self.assertEqual(state, "revoked")

    def test_valid_key_state(self):
        fingerprint, state = key_state(VALID_KEY)
        self.assertEqual(state, "valid")


class UserModelTests(TestCase):

    def test_no_setup_complete(self):
        user = create_and_login_user(self.client)
        self.assertEqual(user.has_setup_complete(), False)

    def test_setup_complete(self):
        user = create_and_login_user(self.client)
        user.public_key = VALID_KEY
        user.fingerprint = VALID_KEY_FINGERPRINT
        user.save()
        self.assertEqual(user.has_setup_complete(), True)


class NotificationsTests(TestCase):

    def setUp(self):
        celery_app.conf.update(task_always_eager=True)

    def test_delete_sent_notifications(self):
        notification = create_notification(sent=True)
        notification_id = notification.id
        self.assertEqual(notification.delete(), False)
        queryset = Notification.objects.filter(id=notification_id)
        self.assertEqual(len(queryset), 1)

    def test_delete_unsent_notification(self):
        notification = create_notification(sent=False)
        notification_id = notification.id
        self.assertNotEqual(notification.delete(), False)
        queryset = Notification.objects.filter(id=notification_id)
        self.assertEqual(len(queryset), 0)

    def test_send_when_group_is_defined(self):
        for i in range(4):
            create_and_login_user(self.client)
        last_user = create_and_login_user(self.client)
        group = Group.objects.create(name="Test Group")
        group.user_set.add(last_user)
        notification = create_notification(sent=False, group=group)
        enqueue_email_notifications(notification.id, notification.send_to.id)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_when_group_is_not_defined(self):
        for i in range(4):
            create_and_login_user(self.client)
        notification = create_notification(sent=False)
        enqueue_email_notifications(notification.id, None)
        self.assertEqual(len(mail.outbox), User.objects.count())
