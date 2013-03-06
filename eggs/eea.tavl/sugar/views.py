from functools import wraps
from django.shortcuts import render, redirect


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
