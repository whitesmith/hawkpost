from django.conf.urls import url
from .views import UpdateSettingsView

urlpatterns = [
    url(r'^settings$', UpdateSettingsView.as_view(), name="humans_update"),
]
