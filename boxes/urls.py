from django.urls import path, re_path
from .views import (BoxListView, BoxCreateView, BoxDeleteView, BoxSubmitView,
                    BoxCloseView)

urlpatterns = [
    path('', BoxListView.as_view(), name="boxes_list"),
    path('create', BoxCreateView.as_view(), name="boxes_create"),
    path('<int:pk>/delete', BoxDeleteView.as_view(), name="boxes_delete"),
    path('<int:pk>/closed', BoxCloseView.as_view(), name="boxes_close"),
    re_path(r'^(?P<box_uuid>[0-9a-z-]+)$', BoxSubmitView.as_view(), name="boxes_show"),
]
