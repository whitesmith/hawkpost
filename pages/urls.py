from django.conf.urls import url
from .views import HomeView, AboutView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name="pages_index"),
    url(r'^about$', AboutView.as_view(), name="pages_about"),
]
