# Andrei Laza, Eau de Web

import logging
import traceback

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Globals import InitializeClass

from naaya.core.zope2util import RestrictedToolkit
from naaya.core.paginator import NaayaPaginator
from Products.NaayaCore.interfaces import ICaptcha
from Products.NaayaBase.constants import PRETTY_EXCEPTION_MSG

log = logging.getLogger(__name__)


class NyCommonView(object):
    """
    This class is for common methods that need to be available for many pages.
    They used to be accessed from NySite via acquisition,
    but that created problems when checking permissions.
    """

    rstk = RestrictedToolkit()

    security = ClassSecurityInfo()

    security.declareProtected(view, 'recaptcha_is_present')

    def recaptcha_is_present(self):
        return ICaptcha(self.getSite()).is_available

    security.declareProtected(view, 'show_recaptcha')

    def show_recaptcha(self, context):
        """ Returns HTML code for reCAPTCHA """
        return ICaptcha(self.getSite()).render_captcha()

    security.declareProtected(view, 'is_valid_recaptcha')

    def is_valid_recaptcha(self, context, REQUEST):
        """ Test if reCaptcha is valid. """
        return ICaptcha(self.getSite()).is_valid_captcha(REQUEST)

    security.declareProtected(view, 'validateCaptcha')

    def validateCaptcha(self, recaptcha_response, REQUEST):
        """
        Deprecated in favour of the `naaya.core.submitter` package.

        Validates recaptcha, returns errors if invalid.
        """
        if self.recaptcha_is_present():
            if not self.is_valid_recaptcha(self, REQUEST):
                return [
                    'The reCaptcha test failed. Please try again.']

    security.declareProtected(view, 'feedback_html')

    def feedback_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_feedback')

    security.declareProtected(view, 'requestrole_html')

    def requestrole_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'site_requestrole')

    security.declareProtected(view, 'channel_details_html')

    def channel_details_html(self, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        kwargs['here'] = self
        return self.getFormsTool().getContent(kwargs, 'channel_details')

    security.declarePublic('standard_error_message')

    def standard_error_message(self, client=None, **kwargs):
        """ """
        try:
            error_log_properties = self.error_log.getProperties()
            ignored_exceptions = error_log_properties['ignored_exceptions']

            if kwargs['error_type'] not in ignored_exceptions:
                try:
                    self.processNotifyOnErrors(kwargs['error_type'],
                                               kwargs['error_value'],
                                               self.REQUEST)

                    self.dumpErrorToJSON(kwargs['error_type'],
                                         kwargs['error_value'])
                except:
                    log.exception('Error processing error')

            if kwargs['error_type'] == 'Redirect':
                return

            site = self.getSite()
            forms_tool = self.getFormsTool()
            tmpl = forms_tool['standard_error_message'].aq_base.__of__(site)
            if kwargs['error_type'] in PRETTY_EXCEPTION_MSG:
                msg = PRETTY_EXCEPTION_MSG[kwargs['error_type']]
                kwargs['error_type'] += '<br /><br />\n\n%s' % msg
            try:
                macro = self.standard_template_macro('light')
                html = tmpl(macro=macro, **kwargs)
            except:
                html = tmpl(macro=None, **kwargs)

            return html

        except:
            try:
                log.exception('Error displaying the error page')
            except:
                pass
            return "Error displaying the error page"

    security.declarePublic('log_page_error')

    def log_page_error(self, error):
        log.warning('Page error: error type %r, error value %r,'
                    ' lineno %r, offset %r, ACTUAL_URL: %s\n%s',
                    error.type, error.value, error.lineno, error.offset,
                    self.REQUEST['ACTUAL_URL'], traceback.format_exc())

    security.declareProtected(view, 'make_paginator')

    def make_paginator(self, *args, **kwargs):
        """ """
        return NaayaPaginator(*args, **kwargs).__of__(self)

InitializeClass(NyCommonView)
