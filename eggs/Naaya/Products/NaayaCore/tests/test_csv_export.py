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
# David Batranu, Eau de Web

from unittest import TestSuite, makeSuite
from StringIO import StringIO

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.contact.contact_item import addNyContact


class NyCSVExportTest(NaayaTestCase):
    """ TestCase for Naaya CSV export """

    def afterSetUp(self):
        addNyFolder(self.portal, 'exported', contributor='contributor', submitted=1)
        addNyFolder(self.portal['exported'], 'contacts', contributor='contributor', submitted=1)
        addNyFolder(self.portal['exported']['contacts'], 'subcontacts', contributor='contributor', submitted=1)
        addNyFolder(self.portal['exported'], 'empty', contributor='contributor', submitted=1)
        self.portal['exported']['contacts'].addNyContact(id='contact1', title='Contact 1', contributor='contributor')
        self.portal['exported']['contacts'].addNyContact(id='contact2', title='Contact 2', contributor='contributor')
        self.portal['exported']['contacts']['subcontacts'].addNyContact(id='subcontact1', title='Subcontact 1', contributor='contributor')
        self.portal['exported']['contacts']['subcontacts'].addNyContact(id='subcontact2', title='Subcontact 2', contributor='contributor')
        
    def beforeTearDown(self):
        self.portal.manage_delObjects(['exported'])
    
    def test_export_all(self):
        export_data = self.portal.exported.csv_export.export(meta_type='Naaya Contact')
        self.assertTrue('Contact 1' in export_data)
        self.assertTrue('Contact 2' in export_data)
        self.assertTrue('Subcontact 1' in export_data)
        self.assertTrue('Subcontact 2' in export_data)
        self.assertEqual(len(export_data.split('\n')), 6)
    
    def test_export_blank(self):
        export_data = self.portal.exported.empty.csv_export.export(meta_type='Naaya Contact')
        self.assertFalse('Contact 1' in export_data)
        self.assertFalse('Contact 2' in export_data)
        self.assertFalse('Subcontact 1' in export_data)
        self.assertFalse('Subcontact 2' in export_data)
        self.assertEqual(len(export_data.split('\n')), 2)
    
    def test_export_contacts(self):
        export_data = self.portal.exported.contacts.csv_export.export(meta_type='Naaya Contact')
        self.assertTrue('Contact 1' in export_data)
        self.assertTrue('Contact 2' in export_data)
        self.assertTrue('Subcontact 1' in export_data)
        self.assertTrue('Subcontact 2' in export_data)
        self.assertEqual(len(export_data.split('\n')), 6)
    
    def test_export_subcontacts(self):
        export_data = self.portal.exported.contacts.subcontacts.csv_export.export(meta_type='Naaya Contact')
        self.assertFalse('Contact 1' in export_data)
        self.assertFalse('Contact 2' in export_data)
        self.assertTrue('Subcontact 1' in export_data)
        self.assertTrue('Subcontact 2' in export_data)
        self.assertEqual(len(export_data.split('\n')), 4)
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyCSVExportTest))
    return suite
