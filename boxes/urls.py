from django.conf.urls import url
from .views import BoxListView, BoxCreateView, BoxDeleteView, BoxSubmitView

urlpatterns = [
    url(r'^$', BoxListView.as_view(), name="boxes_list"),
    url(r'^create$', BoxCreateView.as_view(), name="boxes_create"),
    url(r'^(?P<pk>[0-9]+)/delete$', BoxDeleteView.as_view(), name="boxes_delete"),
    url(r'^(?P<box_uuid>[0-9a-z-]+)$', BoxSubmitView.as_view(), name="boxes_show"),
]
