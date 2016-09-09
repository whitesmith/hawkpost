from django.views.generic import TemplateView
from django.conf import settings

from allauth.account.forms import LoginForm, SignupForm


class AuthMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated():
            context["login_form"] = LoginForm()
            context["signup_form"] = SignupForm()
        return context


class HomeView(AuthMixin, TemplateView):
    """View for the Index page of the website"""
    template_name = "pages/index.html"


class AboutView(AuthMixin, TemplateView):
    """View for the About page of the website"""
    template_name = "pages/about.html"


class HelpView(AuthMixin, TemplateView):
    """View for the About page of the website"""
    template_name = "pages/help.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["support_email"] = settings.SUPPORT_EMAIL
        context["sign_key_url"] = settings.GPG_SIGN_KEY_URL
        return context
