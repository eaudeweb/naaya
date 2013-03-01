from functools import wraps
from django.shortcuts import render
from django.utils.decorators import method_decorator


def authorization_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user:
            return render(request, 'restricted.html')
        return func(*args, **kwargs)
    return wrapper


class AuthorizationRequired(object):

    @method_decorator(authorization_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthorizationRequired, self).dispatch(request, *args,
                                                           **kwargs)