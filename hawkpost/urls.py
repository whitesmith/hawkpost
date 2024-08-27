"""hawkpost URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.utils.decorators import method_decorator

from allauth.account.views import LoginView
from axes.decorators import axes_dispatch
from axes.decorators import axes_form_invalid

from humans.forms import LoginForm

LoginView.dispatch = method_decorator(axes_dispatch)(LoginView.dispatch)
LoginView.form_invalid = method_decorator(
    axes_form_invalid)(LoginView.form_invalid)

urlpatterns = [
    path('admin/login/', admin.site.login),
    re_path(r'^admin/', admin.site.urls),
    path('users/login/', LoginView.as_view(form_class=LoginForm),
        name='account_login'),
    path('users/', include('allauth.urls')),
    path('users/', include('humans.urls')),
    path('box/', include('boxes.urls')),
    path('', include('pages.urls'))
]

urlpatterns += i18n_patterns(
    path('', include('pages.urls')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
