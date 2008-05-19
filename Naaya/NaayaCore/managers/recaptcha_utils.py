"""Small wrappers for Naaya around the captcha Python module which provides
access to reCAPTCHA.
"""

# Python imports
import Captcha as captcha
from xml.sax.saxutils import escape

def render_captcha(context):
    """Return HTML code for CAPTCHA if the current user is anonymous or an empty string otherwise."""
    if not context.isAnonymousUser():
        return ""
    err = context.getSession('err_recaptcha', '')
    context.delSession('err_recaptcha')
    return "".join((captcha.displayhtml(context.getSite().recaptcha_public_key),
                    '<span class="errormsg">',
                    escape(err),
                    '</span>'))

def is_valid_captcha(context, REQUEST):
    """Test if captcha was passed or return True if the user is not anonymous."""
    if not context.isAnonymousUser():
        return True
    is_valid = captcha.submit(REQUEST.get('recaptcha_challenge_field', ''),
                              REQUEST.get('recaptcha_response_field', ''),
                              context.getSite().recaptcha_private_key,
                              REQUEST.get('REMOTE_ADDR', '')).is_valid
    if not is_valid:
        context.setSession('err_recaptcha', 'Incorrect. Try again')
    return is_valid
