from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from humans.models import User
from datetime import timedelta
from .models import Box, Message
from .forms import CreateBoxForm, SubmitBoxForm, MAX_MESSAGE_SIZE
from .tasks import process_email
from .test_constants import ENCRYPTED_MESSAGE
import random
import string


def create_boxes(user):
    not_expired = timezone.now() + timedelta(hours=3)
    expired = timezone.now() - timedelta(hours=3)
    user.own_boxes.create(
        name="open", expires_at=not_expired, status=Box.OPEN)
    user.own_boxes.create(
        name="closed", expires_at=not_expired, status=Box.CLOSED)
    user.own_boxes.create(
        name="sent", expires_at=not_expired, status=Box.DONE)
    user.own_boxes.create(
        name="expired", expires_at=expired, status=Box.EXPIRED)


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
            "expires_at": "12/12/2020 23:00",
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
            "expires_at": "12/12/2020 23:00",
            "max_messages": 1
        }
        form = CreateBoxForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_empty_desription(self):
        """
            Description is optional
        """
        data = {
            "name": "some name",
            "description": "",
            "expires_at": "12/12/2020 23:00",
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
            "expires_at": "12/12/2020 23:00",
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


class MailTaskTests(TestCase):

    def test_email_sending(self):
        """
            With a valid box_id an email is sent and the box status is changed
            to sent
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        initial_box = user.own_boxes.all()[0]
        message = initial_box.messages.create()
        process_email(message.id, {"message": ENCRYPTED_MESSAGE})
        after_box = user.own_boxes.get(id=initial_box.id)
        after_msg = after_box.messages.get(id=message.id)
        #self.assertEqual(message.status, Message.SENT)
        self.assertEqual(after_msg.sent_at, after_box.last_sent_at)
