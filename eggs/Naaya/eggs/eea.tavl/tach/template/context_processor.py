from django.conf import settings


def context(request):
    return {
        'user': request.user,
        'HOSTNAME': settings.HOSTNAME,
    }