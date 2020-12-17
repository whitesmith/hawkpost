from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.core import mail
from humans.models import User
from datetime import timedelta
from .models import Box, Message
from .forms import CreateBoxForm, SubmitBoxForm, MAX_MESSAGE_SIZE
from .tasks import process_email
from .test_constants import ENCRYPTED_MESSAGE
from humans.test_constants import EXPIRED_KEY, EXPIRED_KEY_FINGERPRINT, \
    REVOKED_KEY, REVOKED_KEY_FINGERPRINT, VALID_KEY, VALID_KEY_FINGERPRINT
import random
import string

future_datetime = timezone.now() + timedelta(days=1)
future_datetime_string = future_datetime.strftime("%m/%d/%Y %H:%M")

def create_boxes(user):
    user.own_boxes.create(
        name="open", expires_at=future_datetime, status=Box.OPEN)
    user.own_boxes.create(
        name="closed", expires_at=future_datetime, status=Box.CLOSED)
    user.own_boxes.create(
        name="sent", expires_at=future_datetime, status=Box.DONE)
    past_datetime = timezone.now() - timedelta(days=1)
    user.own_boxes.create(
        name="expired", expires_at=past_datetime, status=Box.EXPIRED)


def create_open_box(user):
    return user.own_boxes.create(name="open",
                                 expires_at=future_datetime,
                                 status=Box.OPEN)


def create_and_login_user(client):
    username = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
    user = User.objects.create_user(username=username,
                                    email="{}@example.com".format(username))
    client.force_login(user)
    return user


class BoxFormTests(TestCase):

    def test_invalid_expiration_date(self):
        """
            Expiration must be submitted provided and with valid format
            If one of this the above statments are not true form must be
            invalid
        """
        data = {
            "name": "some name",
            "description": "some text",
            "expires_at": "31/31/2000 24:00",
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_valid_expiration_date(self):
        """
            If expiration date is valid and in the future form is valid
        """
        data = {
            "name": "some name",
            "description": "some text",
            "expires_at": future_datetime_string,
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_expiration_date_from_past(self):
        """
            If date already belongs to the past, the form must be invalid
        """
        data = {
            "name": "some name",
            "description": "some text",
            "expires_at": "12/12/2012 23:00",
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_empty_name(self):
        """
            Name must be present
        """
        data = {
            "name": "",
            "description": "some text",
            "expires_at": future_datetime_string,
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_empty_description(self):
        """
            Description is optional
        """
        data = {
            "name": "some name",
            "description": "",
            "expires_at": future_datetime_string,
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_invalid_max_messages(self):
        """
            Description is optional
        """
        data = {
            "name": "some name",
            "description": "",
            "expires_at": future_datetime_string,
            "max_messages": 0
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_never_expires(self):
        data = {
            "name": "some name",
            "description": "",
            "never_expires": True,
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), True)


class SubmitBoxFormTests(TestCase):

    def test_encrypted_content(self):
        """
            Form is valid if content is encrypted
        """
        form = SubmitBoxForm({"message": ENCRYPTED_MESSAGE})
        self.assertEqual(form.is_valid(), True)

    def test_clear_text_content(self):
        """
            If not PGP message, form is invalid
        """
        form = SubmitBoxForm({"message": "some clear text message"})
        self.assertEqual(form.is_valid(), False)

    def test_message_too_big(self):
        form = SubmitBoxForm({"message": "m" * (MAX_MESSAGE_SIZE + 1)})
        self.assertEqual(form.is_valid(), False)

    def test_encrypted_file(self):
        form = SubmitBoxForm({"message": ENCRYPTED_MESSAGE,
                              "file_name": "test"})
        self.assertEqual(form.is_valid(), True)

    def test_add_reply_to_is_present(self):
        form = SubmitBoxForm({"message": ENCRYPTED_MESSAGE,
                              "add_reply_to": "on"})
        self.assertEqual(form.is_valid(), True)
        self.assertTrue(form.cleaned_data.get("add_reply_to"))

    def test_add_reply_to_is_not_present(self):
        form = SubmitBoxForm({"message": ENCRYPTED_MESSAGE})
        self.assertEqual(form.is_valid(), True)
        self.assertFalse(form.cleaned_data.get("add_reply_to"))


class BoxListViewTests(TestCase):

    def test_open_boxes_are_default_list(self):
        """
            Base page shows list of open boxes
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        response = self.client.get(reverse("boxes_list"))
        for box in response.context["object_list"]:
            self.assertEqual(box.status, Box.OPEN)

    def test_expired_boxes_list(self):
        """
            With expired query param expired boxes are shown
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        response = self.client.get(reverse("boxes_list"),
                                   {'display': 'Expired'})
        for box in response.context["object_list"]:
            self.assertEqual(box.status, Box.EXPIRED)

    def test_closed_boxes_list(self):
        """
            With closed query param closed boxes are shown
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        response = self.client.get(reverse("boxes_list"),
                                   {'display': 'Closed'})
        for box in response.context["object_list"]:
            self.assertEqual(box.status, Box.CLOSED)

    def test_sent_boxes_list(self):
        """
            With sent query param sent boxes are shown
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        response = self.client.get(reverse("boxes_list"),
                                   {'display': 'Done'})
        for box in response.context["object_list"]:
            self.assertEqual(box.status, Box.DONE)


class BoxSubmitViewTests(TestCase):

    def test_valid_owner_key(self):
        user = create_and_login_user(self.client)
        user.public_key = VALID_KEY
        user.fingerprint = VALID_KEY_FINGERPRINT
        user.save()
        box = create_open_box(user)
        response = self.client.get(reverse("boxes_show", args=(box.uuid,)))
        self.assertEqual(response.template_name[0], 'boxes/box_submit.html')

    def test_revoked_owner_key(self):
        user = create_and_login_user(self.client)
        user.public_key = REVOKED_KEY
        user.fingerprint = REVOKED_KEY_FINGERPRINT
        user.save()
        box = create_open_box(user)
        response = self.client.get(reverse("boxes_show", args=(box.uuid,)))
        self.assertEqual(response.template_name, 'boxes/closed.html')

    def test_expired_owner_key(self):
        user = create_and_login_user(self.client)
        user.public_key = EXPIRED_KEY
        user.fingerprint = EXPIRED_KEY_FINGERPRINT
        user.save()
        box = create_open_box(user)
        response = self.client.get(reverse("boxes_show", args=(box.uuid,)))
        self.assertEqual(response.template_name, 'boxes/closed.html')

    def test_no_owner_key(self):
        user = create_and_login_user(self.client)
        box = create_open_box(user)
        user.save()
        response = self.client.get(reverse("boxes_show", args=(box.uuid,)))
        self.assertEqual(response.template_name, 'boxes/closed.html')

    def test_box_not_found(self):
        user = create_and_login_user(self.client)
        user.public_key = VALID_KEY
        user.fingerprint = VALID_KEY_FINGERPRINT
        user.save()
        box = create_open_box(user)
        box.delete()
        response = self.client.get(reverse("boxes_show", args=(box.uuid,)))
        self.assertEqual(response.status_code, 404)


class BoxCreateViewTests(TestCase):

    def test_create_new_box(self):
        user = create_and_login_user(self.client)
        user.public_key = VALID_KEY
        user.fingerprint = VALID_KEY_FINGERPRINT
        user.save()
        response = self.client.post(reverse("boxes_create"), {
                                    "name": "test",
                                    "never_expires": True,
                                    "max_messages": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.boxes.count(), 1)
        self.assertEqual(user.boxes.first().name, "test")


class BoxDeleteViewTests(TestCase):

    def test_delete_existing_box(self):
        user = create_and_login_user(self.client)
        create_boxes(user)
        box = user.own_boxes.filter(name="open").first()
        response = self.client.post(reverse("boxes_delete", args=(box.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.own_boxes.count(), 3)

    def test_cannot_delete_box_that_are_not_open(self):
        user = create_and_login_user(self.client)
        create_boxes(user)
        box = user.own_boxes.filter(name="closed").first()
        response = self.client.post(reverse("boxes_delete", args=(box.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.own_boxes.count(), 4)


class BoxCloseView(TestCase):

    def test_close_an_open_box(self):
        user = create_and_login_user(self.client)
        create_boxes(user)
        box = user.own_boxes.filter(name="open").first()
        response = self.client.post(reverse("boxes_close", args=(box.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.own_boxes.filter(status=Box.CLOSED).count(), 2)

    def test_close_box_that_is_not_open(self):
        user = create_and_login_user(self.client)
        create_boxes(user)
        box = user.own_boxes.filter(name="sent").first()
        response = self.client.post(reverse("boxes_close", args=(box.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.own_boxes.filter(status=Box.CLOSED).count(), 1)


class MailTaskTests(TestCase):

    def test_email_sending(self):
        """
            With a valid message_id an email is sent and the Message status
            is changed to sent
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        initial_box = user.own_boxes.all()[0]
        message = initial_box.messages.create()
        process_email(message.id, {"message": ENCRYPTED_MESSAGE})
        after_box = user.own_boxes.get(id=initial_box.id)
        after_msg = after_box.messages.get(id=message.id)
        message.refresh_from_db()
        self.assertEqual(message.status, Message.SENT)
        self.assertEqual(after_msg.sent_at, after_box.last_sent_at)
        self.assertEqual(len(mail.outbox[0].reply_to), 0)

    def test_email_sending_with_reply_to(self):
        mail.outbox = []
        user = create_and_login_user(self.client)
        create_boxes(user)
        initial_box = user.own_boxes.all()[0]
        message = initial_box.messages.create()
        process_email(
            message.id, {"message": ENCRYPTED_MESSAGE}, sent_by=user.email
        )
        message.refresh_from_db()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email, mail.outbox[0].reply_to)
        self.assertEqual(message.status, Message.SENT)
