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
# Alex Morega, Eau de Web

from unittest import TestSuite, makeSuite

from DateTime import DateTime
from Testing import ZopeTestCase
from Products.Naaya.tests import NaayaTestCase, NaayaFunctionalTestCase

from Products.NaayaCore.SchemaTool.Schema import Schema

class SchemaAdminTest(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
    """ Functional TestCase for Naaya Schema Tool administration interface """

    def afterSetUp(self):
        self.browser_do_login('admin', '')

    def beforeTearDown(self):
        self.browser_do_logout()

    def test_schemas_list(self):
        self.browser.go('http://localhost/portal/portal_schemas/admin_html')

        html = self.browser.get_html()
        self.failUnless('<h1>Manage content types</h1>' in html)

        self.failUnless('HTML Document' in html)
        self.failUnless('portal_schemas/NyDocument/admin_html' in html)

    def test_schema(self):
        self.browser.go('http://localhost/portal/portal_schemas/NyDocument/admin_html')

        html = self.browser.get_html()
        self.failUnless('<h1>Manage content types - HTML Document</h1>' in html)

        self.failUnless('Title' in html)
        self.failUnless('portal_schemas/NyDocument/title-property/admin_html' in html)
        self.failUnless('Release date' in html)
        self.failUnless('portal_schemas/NyDocument/releasedate-property/admin_html' in html)

    def test_schema_widget(self):
        self.browser.go('http://localhost/portal/portal_schemas/NyDocument/title-property/admin_html')

        html = self.browser.get_html()
        self.failUnless('<h1>Manage content types - HTML Document - title</h1>' in html)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SchemaAdminTest))
    return suite
