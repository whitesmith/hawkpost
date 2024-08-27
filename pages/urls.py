from django.urls import path
from .views import HomeView, AboutView, HelpView

urlpatterns = [
    path('', HomeView.as_view(), name="pages_index"),
    path('about', AboutView.as_view(), name="pages_about"),
    path('help', HelpView.as_view(), name="pages_help")
]
