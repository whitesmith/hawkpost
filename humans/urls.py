from django.urls import path
from .views import UpdateSettingsView, DeleteUserView

urlpatterns = [
    path('settings', UpdateSettingsView.as_view(), name="humans_update"),
    path('delete', DeleteUserView.as_view(), name="humans_delete"),
]
