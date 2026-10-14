# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
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
        # FunctionalDocFileSuite bypasses _callSetUp(), so take the fixtures
        # from the layer here
        layer = type(self).layer
        self.app = layer._current_app
        self.portal = layer._current_portal
        self.fake_request = layer._current_fake_request
        self.mail_log = layer._mail_log
        self.wsgi_request = layer._tzope.wsgi_app
        populate_threading_local(self.portal, self.portal.REQUEST)
        self.portal.REQUEST['PARENTS'] = [self.portal, self.app]
        super().setUp()

    def loadFile(self, name):
        """ Upload-like file object for a file in this directory """
        from io import BytesIO
        with open(os.path.join(self.home, name), 'rb') as f:
            data = BytesIO(f.read())
        data.filename = os.path.basename(name)
        return data

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
        Suite('doc/usage.txt',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaPhotoArchive',
              test_class=CustomFunctionalTestCase),
        Suite('doc/content.txt',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaPhotoArchive',
              test_class=CustomFunctionalTestCase),
          ))
