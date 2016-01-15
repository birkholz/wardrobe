from django.utils import timezone


class TimezoneMiddleware(object):
    @staticmethod
    def process_request(request):
        tz = request.session.get('django_timezone')
        if tz:
            timezone.activate(tz)
        else:
            timezone.activate(timezone.get_default_timezone())
            if request.user.is_authenticated():
                if request.user.prefs.time_zone:
                    timezone.activate(request.user.prefs.time_zone)
