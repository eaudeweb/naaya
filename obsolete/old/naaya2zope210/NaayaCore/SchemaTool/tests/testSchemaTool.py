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
from Products.Naaya.tests import NaayaTestCase

from Products import NaayaContent

class NaayaSchemaToolTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Schema Tool """

    def test_tool_in_new_site(self):
        """ make sure the SchemaTool is instantiated in a new NySite """
        self.failUnless('portal_schemas' in self.portal.objectIds())
        self.failUnlessEqual(self.portal.portal_schemas.title, 'Portal schemas')

        initial_schemas = set(self.portal.portal_schemas.objectIds())
        expected_schemas = set(['NyDocument', 'NyEvent', 'NyExFile', 'NyFile',
                'NyGeoPoint', 'NyMediaFile', 'NyNews', 'NyPointer', 'NyStory', 'NyURL'])
        self.failUnless(expected_schemas.issubset(initial_schemas))

    def test_getSchemaForMetatype(self):
        tool = self.portal.portal_schemas
        self.failUnlessEqual(tool.NyDocument, tool.getSchemaForMetatype('Naaya Document'))
        self.failUnlessEqual(tool.getSchemaForMetatype('No Such Type'), None)

    def test_listSchemas(self):
        schemas = self.portal.portal_schemas.listSchemas()
        self.failUnless('Naaya Document' in schemas.keys())
        self.failUnless(schemas['Naaya Document'].absolute_url()
            == self.portal.portal_schemas.NyDocument.absolute_url())


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaSchemaToolTestCase))
    return suite
