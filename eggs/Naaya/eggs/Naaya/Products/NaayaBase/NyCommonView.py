# Andrei Laza, Eau de Web

import logging
import traceback
from cStringIO import StringIO

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Globals import InitializeClass
from zope.deprecation import deprecate

from naaya.core.zope2util import RestrictedToolkit
from naaya.core.paginator import NaayaPaginator

from Products.NaayaCore.interfaces import ICaptcha
from Products.NaayaCore.managers.captcha_tool import captcha_tool

class NyCommonView(object):
    """
    This class is for common methods that need to be available for many pages.
    They used to be accessed from NySite via acquisition,
    but that created problems when checking permissions.
    """
    rstk = RestrictedToolkit()

    security = ClassSecurityInfo()

    security.declareProtected(view, 'getCaptcha')
    def getCaptcha(self):
        """ generate a Captcha image """
        g = captcha_tool()
        g.defaultSize = (100, 20)
        i = g.render()
        newimg = StringIO()
        i.save(newimg, "JPEG")
        newimg.seek(0)
        #set the word on session
        self.setSession('captcha', g.solutions[0])
        return newimg.getvalue()

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
    def validateCaptcha(self, contact_word, REQUEST):
        """
        Deprecated in favour of the `naaya.core.submitter` package.

        Validates captcha or recaptcha, returns errors if invalid.
        """
        if self.recaptcha_is_present():
            if not self.is_valid_recaptcha(self, REQUEST):
                return ['Verification words do not match the ones in the picture.']
        else:
            if contact_word != self.getSession('captcha', ''):
                self.delSession('captcha')
                return ['The word you typed does not match with the one shown in the image. Please try again.']

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
    def standard_error_message(self, client=None, REQUEST=None, **kwargs):
        """ """
        kwargs['here'] = self
        return self.getFormsTool().getContent(kwargs, 'standard_error_message')

    security.declarePublic('log_page_error')
    def log_page_error(self, error):
        log = logging.getLogger('naaya.commonview.page_error')
        log.warning('Page error: error type %r, error value %r,'
                    ' lineno %r, offset %r\n%s',
                    error.type, error.value, error.lineno, error.offset,
                    traceback.format_exc())

    security.declareProtected(view, 'make_paginator')
    def make_paginator(self, *args, **kwargs):
        """ """
        return NaayaPaginator(*args, **kwargs).__of__(self)

InitializeClass(NyCommonView)
