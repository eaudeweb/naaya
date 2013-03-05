from functools import wraps
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user:
            return render(request, 'restricted.html')
        return func(*args, **kwargs)
    return wrapper


def auth_details_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.country:
            return redirect('overview')
        return func(*args, **kwargs)
    return wrapper


class AuthRequired(object):

    @method_decorator(auth_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthRequired, self).dispatch(request, *args, **kwargs)


class AuthDetailsRequired(object):

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthDetailsRequired, self).dispatch(request, *args, **kwargs)

