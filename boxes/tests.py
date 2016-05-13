from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from humans.models import User
from datetime import timedelta
from .models import Box
from .forms import CreateBoxForm, SubmitBoxForm
from .tasks import process_email
import random
import string


ENCRYPTED_MESSAGE = """-----BEGIN PGP MESSAGE-----\r
Version: OpenPGP.js v2.2.0\r
Comment: http://openpgpjs.org\r
\r
wcFMA9K5fTFi5lXtAQ//WLWrSXgc5YRgL8sGCLPFVoFb5ootYlCphhk+hWSD\r
Wr7U4IXYr+mHvhX3twigK+io4EVoBtSg5+e+Nkvbj4HTIq/XH2DGHLFDMKTc\r
zeY7kNHxKuWB4ZCDJPTlwQHfY5hyBZQTkhRDXsA4Y79OZo9gN9FwvbKjSwUM\r
AG+fhorLT/nEoHexZt1vohhobAQkRaVLh+NMKRLgHXdhPhbO92JIvel/TwZs\r
5Iub8S11bOOsbT4a6y9yxQk2rL8lct77nygjlrK6ejlwdHWzT6OG3yS1YoaK\r
jpx3frXnITCgy8oNPn1Pxn4S7Pmmq4xl4JmH4inmlzRMZDzKG/5kVesh6pwH\r
nJyJCMuyIj60gNhxBF91ndLgg+PJWwjZ3I+E/M5mo0ZscCpAnxKh/qmt4I6j\r
rn/jEp1djY6nFGmuzmHIGYjhvxkGFfFEIwsqkHfGTBOkWIjK5T4WzpGNa4Dr\r
k285x1R+3lzUBzl674Rl74+8wLm9DESd3k6+yOhibkv29kVxEcaCsOOzpNOx\r
q/1vWCRjqoOnVXrx3tbzpjLjb647Hf/+DYA6ENpNyohAZv9bp3J1ZTrcpMXg\r
/6mOxDt+C3G5ARmH/FG6JYtge1ck4GQh02CQxiYG8psaqAntd+VzaRUl+lVC\r
1pbvd9ToxWD3HaVdoGsZBEjIWt9gEtCv+RTvPY6EmrbSPQGI40HjcYG8sbY+\r
OZ/Lsv1Kz9Rg/VSvCxknTCncdju07kD5eiLJUAt1u6JYd4mn/TGZBlmtRo/J\r
CIuqkcg=\r
=6WtN\r
-----END PGP MESSAGE-----"""


def create_boxes(user):
    not_expired = timezone.now() + timedelta(hours=3)
    expired = timezone.now() - timedelta(hours=3)
    user.own_boxes.create(
        name="open", expires_at=not_expired, status=Box.OPEN)
    user.own_boxes.create(
        name="closed", expires_at=not_expired, status=Box.CLOSED)
    user.own_boxes.create(
        name="onqueue", expires_at=not_expired, status=Box.ONQUEUE)
    user.own_boxes.create(
        name="sent", expires_at=not_expired, status=Box.SENT)
    user.own_boxes.create(
        name="expired", expires_at=expired, status=Box.EXPIRED)


def create_and_login_user(client):
    username = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
    user = User.objects.create_user(username=username)
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
            "expires_at": "31/31/2000 24:00"
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
            "expires_at": "12/12/2020 23:00"
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
            "expires_at": "12/12/2012 23:00"
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
            "expires_at": "12/12/2020 23:00"
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
            "expires_at": "12/12/2020 23:00"
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
                                   {'display': 'Sent'})
        for box in response.context["object_list"]:
            self.assertEqual(box.status, Box.SENT)

    def test_on_queue_boxes_list(self):
        """
            With on queue query param queue boxes are shown
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        response = self.client.get(reverse("boxes_list"),
                                   {'display': 'On Queue'})
        for box in response.context["object_list"]:
            self.assertEqual(box.status, Box.ONQUEUE)


class MailTaskTests(TestCase):

    def test_email_sending(self):
        """
            With a valid box_id an email is sent and the box status is changed
            to sent
        """
        user = create_and_login_user(self.client)
        create_boxes(user)
        initial_box = user.own_boxes.all()[0]
        process_email(initial_box.id, {"message": ENCRYPTED_MESSAGE})
        after_box = user.own_boxes.get(id=initial_box.id)
        self.assertEqual(after_box.status, Box.SENT)
