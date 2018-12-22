from django.views.generic import TemplateView
from django.conf import settings
from humans.views import AuthMixin


class HomeView(AuthMixin, TemplateView):
    """View for the Index page of the website"""
    template_name = "pages/index.html"


class AboutView(AuthMixin, TemplateView):
    """View for the About page of the website"""
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin_name"] = settings.SUPPORT_NAME
        context["admin_email"] = settings.SUPPORT_EMAIL
        context["description"] = settings.INSTANCE_DESCRIPTION
        context["version"] = settings.VERSION
        return context


class HelpView(AuthMixin, TemplateView):
    """View for the About page of the website"""
    template_name = "pages/help.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["support_email"] = settings.SUPPORT_EMAIL
        return context
