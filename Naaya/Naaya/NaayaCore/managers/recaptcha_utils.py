#A plugin for reCAPTCHA. Provides a CAPTCHA for Python using the reCAPTCHA service.
#Does not require any imaging libraries because the CAPTCHA is served directly from reCAPTCHA.
#This library requires one API key from http://recaptcha.net/api/getkey.
"""Small wrappers for Naaya around the captcha Python module which provides
access to reCAPTCHA.
"""

# Python imports
from xml.sax.saxutils import escape
import urllib2, urllib

API_SSL_SERVER="https://api-secure.recaptcha.net"
API_SERVER="http://api.recaptcha.net"
VERIFY_SERVER="api-verify.recaptcha.net"

def render_captcha(context):
    """
    Return HTML code for CAPTCHA if the current user does not have
    the SKIP_CAPTCHA permission or an empty string otherwise
    """
    if context.checkPermissionSkipCaptcha():
        return ""
    err = context.getSession('err_recaptcha', '')
    context.delSession('err_recaptcha')
    return "".join((displayhtml(context.getSite().recaptcha_public_key),
                    '<span class="errormsg">',
                    escape(err),
                    '</span>'))

def is_valid_captcha(context, REQUEST):
    """Test if captcha was passed or return True if the user is not anonymous."""
    if context.checkPermissionSkipCaptcha():
        return True
    is_valid = submit(REQUEST.get('recaptcha_challenge_field', ''),
                      REQUEST.get('recaptcha_response_field', ''),
                      context.getSite().recaptcha_private_key,
                      REQUEST.get('REMOTE_ADDR', '')).is_valid
    if not is_valid:
        context.setSession('err_recaptcha', 'Incorrect. Try again')
    return is_valid

class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code

def displayhtml (public_key,
                 use_ssl = False,
                 error = None):
    """Gets the HTML to display for reCAPTCHA

    public_key -- The public api key
    use_ssl -- Should the request be sent over ssl?
    error -- An error message to display (from RecaptchaResponse.error_code)"""

    error_param = ''
    if error:
        error_param = '&error=%s' % error

    if use_ssl:
        server = API_SSL_SERVER
    else:
        server = API_SERVER

    return """<script type="text/javascript" src="%(ApiServer)s/challenge?k=%(PublicKey)s%(ErrorParam)s"></script>

<noscript>
           <iframe src="%(ApiServer)s/noscript?k=%(PublicKey)s%(ErrorParam)s" height="300" width="500" frameborder="0"></iframe><br />
           <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
           <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
</noscript>
""" % {
    'ApiServer' : server,
    'PublicKey' : public_key,
    'ErrorParam' : error_param,
}


def submit (recaptcha_challenge_field,
            recaptcha_response_field,
            private_key,
            remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from the form
    recaptcha_response_field -- The value of recaptcha_response_field from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
        return RecaptchaResponse (is_valid = False, error_code = 'incorrect-captcha-sol')



    params = urllib.urlencode ({
        'privatekey': private_key,
        'remoteip' : remoteip,
        'challenge': recaptcha_challenge_field,
        'response' : recaptcha_response_field,
    })

    request = urllib2.Request (
        url = "http://%s/verify" % VERIFY_SERVER,
        data = params,
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
        }
    )

    httpresp = urllib2.urlopen (request)

    return_values = httpresp.read ().splitlines ();
    httpresp.close();

    return_code = return_values [0]

    if (return_code == "true"):
        return RecaptchaResponse (is_valid=True)
    else:
        return RecaptchaResponse (is_valid=False, error_code = return_values [1])
