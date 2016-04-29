from django.utils import timezone


class TimezoneMiddleware():
    def process_request(self, request):
        if request.user.is_authenticated():
            tzname = request.user.timezone
            if tzname:
                timezone.activate(tzname)
            else:
                timezone.deactivate()
