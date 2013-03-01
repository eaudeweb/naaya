from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader

import requests
from threading import local


_thread_locals = local()
def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_forwarded_cookies(request):
    forwarded_cookies = {}
    for name in getattr(settings, 'FRAME_COOKIES', []):
        if name in request.COOKIES:
            forwarded_cookies[name] = request.COOKIES[name]
    return forwarded_cookies


class RequestMiddleware(object):
    """
    Middleware that gets various objects from the
    request object and saves them in thread local storage.
    """
    def process_request(self, request):
        _thread_locals.request = request


class UserMiddleware(object):

    def process_request(self, request):
        request = get_current_request()
        if getattr(settings, 'FRAME_URL', None):
            forwarded_cookies = get_forwarded_cookies(request)
            resp = requests.get(settings.FRAME_URL, cookies=forwarded_cookies)
            if (resp.status_code == 200 and resp.json()):
                request.user_id = resp.json()['user_id']
                request.user_roles = resp.json()['user_roles']
                # request.user_roles = ['Authenticated']


class Loader(BaseLoader):
    is_usable = True

    def _process_resp(self, html):
        substitutions = [
            ("{%", "{% templatetag openblock %}"),
            ("%}", "{% templatetag closeblock %}"),
            ("{{", "{% templatetag openvariable %}"),
            ("}}", "{% templatetag closevariable %}"),
            ("<!-- block_messages -->",
                "{% block action_buttons %}{% endblock %}"
                "{% block messages %}{% endblock %}"),
            ("<!-- block_content -->",
                "{% block content %}{% endblock %}"),
            ("<!-- block_head -->",
                "{% block head %}{% endblock %}"),
        ]

        html = html.strip()
        for sub_a, sub_b in substitutions:
            html = html.replace(sub_a, sub_b)
        return html

    def load_template_source(self, template_name, template_dirs=None):
        request = get_current_request()

        if (request and getattr(settings, 'FRAME_URL', None)
            and template_name == 'frame.html' ):

            forwarded_cookies = get_forwarded_cookies(request)

            resp = requests.get(settings.FRAME_URL, cookies=forwarded_cookies)
            if (resp.status_code == 200 and resp.json()):
                frame_response = self._process_resp(resp.json()['frame_html'])
                return frame_response, template_name

        raise TemplateDoesNotExist

    load_template_source.is_usable = True

_loader = Loader()