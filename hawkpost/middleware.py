from django.utils import timezone


class TimezoneMiddleware():
    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(request.user.timezone)
        else:
            timezone.deactivate()
