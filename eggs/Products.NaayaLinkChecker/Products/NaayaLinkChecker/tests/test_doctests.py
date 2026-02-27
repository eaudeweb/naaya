""" Doc tests
"""
import doctest
import unittest
import os
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase
from naaya.i18n.patches import populate_threading_local

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class CustomFunctionalTestCase(FunctionalTestCase):
    home = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        # FunctionalDocFileSuite calls setUp() directly, bypassing
        # _callSetUp() which normally injects portal/app/etc from
        # the layer.  Do the injection here so that doctest globs
        # (and self.portal) are available.
        layer = type(self).layer
        self.app = layer._current_app
        self.portal = layer._current_portal
        self.fake_request = layer._current_fake_request
        self.mail_log = layer._mail_log
        self.wsgi_request = layer._tzope.wsgi_app
        populate_threading_local(self.portal, self.portal.REQUEST)
        self.portal.REQUEST['PARENTS'] = [self.portal, self.app]
        super().setUp()

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
        Suite('Utils.py',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaLinkChecker',
              test_class=CustomFunctionalTestCase),
        Suite('doc/functionality.txt',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaLinkChecker',
              test_class=CustomFunctionalTestCase),
          ))
