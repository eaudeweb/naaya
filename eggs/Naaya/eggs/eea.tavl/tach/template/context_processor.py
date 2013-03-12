from django.conf import settings


def context(request):
    return {
        'account': request.account,
        'HOSTNAME': settings.HOSTNAME,
    }