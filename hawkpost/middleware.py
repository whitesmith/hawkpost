from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            timezone.activate(request.user.timezone)
        else:
            timezone.deactivate()


class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            translation.activate(request.user.language)
