from django.views.generic import TemplateView


class HomeView(TemplateView):
    """View for the Index page of the website"""
    template_name = "pages/index.html"


class AboutView(TemplateView):
    """View for the Index page of the website"""
    template_name = "pages/about.html"
