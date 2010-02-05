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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

#Python imports
import os
from unittest import TestSuite, makeSuite

#Zope imports
from Globals import package_home

#Naaya imports
from naaya.core.StaticServe import StaticServeFromFolder
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from naaya.content.document import NyDocument


class StaticServeFromFolderTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        NyDocument.test_static_serve = StaticServeFromFolder('static_serve', globals(), cache=False)

    def beforeTearDown(self):
        del NyDocument.test_static_serve

    def test_a_html(self):
        file_path = os.path.join(package_home(globals()), 'static_serve/a.html')
        fd = open(file_path)
        read_data = fd.read()
        fd.close()

        url = 'http://localhost/portal/info/contact/test_static_serve/a.html'
        self.browser.go(url)
        server_data = self.browser.get_html()

        self.assertEqual(read_data, server_data)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(StaticServeFromFolderTest))
    return suite

