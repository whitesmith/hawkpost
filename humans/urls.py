from django.conf.urls import url
from .views import UpdateSettingsView, DeleteUserView

urlpatterns = [
    url(r'^settings$', UpdateSettingsView.as_view(), name="humans_update"),
    url(r'^delete$', DeleteUserView.as_view(), name="humans_delete"),
]
