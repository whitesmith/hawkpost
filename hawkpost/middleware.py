from django.utils import timezone, translation


class TimezoneMiddleware():
    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(request.user.timezone)
        else:
            timezone.deactivate()

class LanguageMiddleware():
    def process_request(self, request):
        if request.user.is_authenticated():
            translation.activate(request.user.language)
