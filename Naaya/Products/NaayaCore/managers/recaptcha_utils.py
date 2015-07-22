"""A plugin for reCAPTCHA. Provides a CAPTCHA for Python using the reCAPTCHA
service. Does not require any imaging libraries because the CAPTCHA is served
directly from reCAPTCHA. This library requires one API key from
http://google.com/recaptcha.
Small wrappers for Naaya around the captcha Python module which provides
access to reCAPTCHA.
"""

# Python imports
from xml.sax.saxutils import escape
import urllib
import urllib2
import simplejson as json

API_JS = "https://www.google.com/recaptcha/api.js"
VERIFY_SERVER = "https://www.google.com/recaptcha/api/siteverify"


def render_captcha(context):
    """Return HTML code for CAPTCHA."""
    err = context.getSession('err_recaptcha', '')
    context.delSession('err_recaptcha')
    return "".join(('<p class="message-error">',
                    escape(err),
                    '</p>',
                    displayhtml(context.getSite().get_recaptcha_public_key())))


def is_valid_captcha(context, REQUEST):
    """Test if captcha was passed."""
    is_valid = submit(REQUEST.get('g-recaptcha-response', ''),
                      context.getSite().get_recaptcha_private_key(),
                      REQUEST.get('REMOTE_ADDR', '')).is_valid
    if not is_valid:
        context.setSession(
            'err_recaptcha',
            'Your previous attempt was incorrect. Please try again')
    return is_valid


class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code


def displayhtml(public_key,
                use_ssl=False,
                error=None):
    """Gets the HTML to display for reCAPTCHA"""

    return """<script type="text/javascript" src="%(ApiJS)s"></script>

            <div class="g-recaptcha" data-sitekey="%(PublicKey)s"></div>
        """ % {'ApiJS': API_JS,
               'PublicKey': public_key,
               }


def submit(recaptcha_response_field,
           private_key,
           remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from
                                 the form
    recaptcha_response_field -- The value of recaptcha_response_field from
                                the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """

    if not (recaptcha_response_field and len(recaptcha_response_field)):
        return RecaptchaResponse(is_valid=False,
                                 error_code='incorrect-captcha-sol')

    params = urllib.urlencode({
        'secret': private_key,
        'remoteip': remoteip,
        'response': recaptcha_response_field,
    })

    request = urllib2.Request(
        url=VERIFY_SERVER,
        data=params,
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
        }
    )

    httpresp = json.load(urllib2.urlopen(request))

    return_code = httpresp['success']

    if return_code is True:
        return RecaptchaResponse(is_valid=True)
    else:
        return RecaptchaResponse(is_valid=False,
                                 error_code=httpresp.get('error_codes'))

from Products.Naaya.interfaces import INySite
from Products.NaayaCore.interfaces import ICaptcha
from zope.interface import implements
from zope.component import adapts


class CaptchaProvider(object):
    implements(ICaptcha)
    adapts(INySite)

    def __init__(self, site):
        self.site = site

    @property
    def is_available(self):
        return (self.site.get_recaptcha_private_key() and
                self.site.get_recaptcha_public_key())

    def render_captcha(self):
        return render_captcha(self.site)

    def is_valid_captcha(self, request):
        return is_valid_captcha(self.site, request)
