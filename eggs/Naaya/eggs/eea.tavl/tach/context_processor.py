from django.conf import settings

def util(request):
    return {
        'HOSTNAME': settings.HOSTNAME,
    }
