from django.test import TestCase
from django.urls import reverse
from django.conf import settings


class TestPages(TestCase):
    """Some very redimentary tests to make sure pages are being delivered."""

    def test_help_page_rendered(self):
        response = self.client.get(reverse("pages_help"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("pages/help.html", [t.name for t in response.templates])
        self.assertEqual(
            response.context["support_email"], settings.SUPPORT_EMAIL)

    def test_about_page_rendered(self):
        response = self.client.get(reverse("pages_about"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("pages/about.html", [t.name for t in response.templates])
        self.assertEqual(
            response.context["admin_name"], settings.SUPPORT_NAME)
        self.assertEqual(
            response.context["admin_email"], settings.SUPPORT_EMAIL)
        self.assertEqual(
            response.context["description"], settings.INSTANCE_DESCRIPTION)
        self.assertEqual(
            response.context["version"], settings.VERSION)

    def test_home_page_rendered(self):
        response = self.client.get(reverse("pages_index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("pages/index.html", [t.name for t in response.templates])
