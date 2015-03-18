"""
Check captcha and/or user name and email.

The normal case for submitting content is by authenticated, trusted
users. Sometimes we want to accept contributions from a wider public,
but then we need to require a captcha, and/or require people to
submit name and email, so the site admins can trace who contributed
the content.

"""

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.AuthenticationTool.AuthenticationTool \
    import is_anonymous
from naaya.core.utils import is_valid_email


def info_required(parent, request):
    """ What information do we require from this submitter?  """
    return {
        'captcha': not parent.checkPermissionSkipCaptcha(),
        'name_and_email': is_anonymous(request.AUTHENTICATED_USER),
    }

_info_html = NaayaPageTemplateFile('zpt/submitter_info', globals(),
                                   'naaya.core.submitter.info_html')


def info_html(parent, request):
    """ Render the HTML to request captcha and/or name + email. """
    required = info_required(parent, request)
    return _info_html.__of__(parent)(required=required)


def info_check(parent, request, ob):
    """
    Receive and check what the user entered; save the name & email on
    the newly created object.
    """

    errors = {}
    required = info_required(parent, request)

    # check Captcha/reCaptcha
    if required['captcha']:
        recaptcha_response = request.form.get('g-recaptcha-response', '')
        captcha_errors = parent.validateCaptcha(recaptcha_response, request)
        if captcha_errors:
            errors['captcha'] = captcha_errors

    # check name/email, if they are required
    if required['name_and_email']:
        info = {
            'name': request.form.get('submitter-name', ''),
            'email': request.form.get('submitter-email', ''),
        }

        request.SESSION['submitter-info'] = info

        name_and_email_errors = {}
        if not info['name']:
            name_and_email_errors['submitter-name'] = (
                ["Submitter name is mandatory"])
        if not info['email']:
            name_and_email_errors['submitter-email'] = (
                ["Submitter email is mandatory"])
        elif not is_valid_email(info['email']):
            name_and_email_errors['submitter-email'] = (
                ["Invalid email address"])

        if name_and_email_errors:
            errors.update(name_and_email_errors)
        else:
            ob.submitter_info = info

    return errors
