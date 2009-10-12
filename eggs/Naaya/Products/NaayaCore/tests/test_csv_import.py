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
from StringIO import StringIO

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

csv_data = ('Title,Description,Automatically redirect to the given URL,URL\n'
    'My URL 1,The best URL,no,http://example.com\n'
    'Eau de Web,The Naaya company,yes,http://www.eaudeweb.ro\n')

def check_uploaded(test):
    test.failUnlessEqual(len(test.portal.imported.objectIds()), 2)
    test.failUnlessEqual(set(map(lambda url: url.title, test.portal.imported.objectValues())),
        set(['My URL 1', 'Eau de Web']))
    test.failUnlessEqual(set(map(lambda url: url.locator, test.portal.imported.objectValues())),
        set(['http://example.com', 'http://www.eaudeweb.ro']))
    test.failUnlessEqual(test.portal.imported._getOb('my-url-1').redirect, False)
    test.failUnlessEqual(test.portal.imported._getOb('eau-de-web').redirect, True)

class NyCSVImportTest(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'imported', contributor='contributor', submitted=1)

    def beforeTearDown(self):
        self.portal.manage_delObjects(['imported'])

    def test_generate_csv_template(self):
        columns = self.portal.csv_import.template('Naaya URL').strip().split(',')
        self.failUnlessEqual(len(columns), 13)
        self.failUnless('Title' in columns)
        self.failUnless('Description' in columns)
        self.failUnless('Automatically redirect to the given URL' in columns)
        self.failUnless('URL' in columns)

    def test_import_ok(self):
        self.portal.imported.csv_import.do_import(meta_type='Naaya URL',
            data=StringIO(csv_data))
        check_uploaded(self)

    def test_import_document(self):
        data = ('Title,Description,Geographical coverage,Keywords,Sort order,'
                'Release date,Open for comments,Body (HTML)\n'
            'My doc,,,,,,,This is a test document.\n')
        self.portal.imported.csv_import.do_import(meta_type='Naaya Document',
            data=StringIO(data))
        self.failUnless('my-doc' in self.portal.imported.objectIds())
        my_doc = self.portal.imported._getOb('my-doc')
        self.failUnlessEqual(my_doc.meta_type, 'Naaya Document')
        self.failUnlessEqual(my_doc.title, 'My doc')
        self.failUnlessEqual(my_doc.body, 'This is a test document.')
        self.failUnlessEqual(my_doc.sortorder, 100)
        self.failUnless(my_doc.approved)

    def test_import_unicode_document(self):
        data = ('Title,Description,Geographical coverage,Keywords,Sort order,'
                'Release date,Open for comments,Body (HTML)\n'
            'Forschungsinstitut f\xc3\xbcr Freizeit und Tourismus (FIF),,,,,,,This is a test document.\n')
        self.portal.imported.csv_import.do_import(meta_type='Naaya Document',
            data=StringIO(data))
        self.failUnless('forschungsinstitut-fur-freizeit-und-tourismus-fif' in self.portal.imported.objectIds())
        my_doc = self.portal.imported._getOb('forschungsinstitut-fur-freizeit-und-tourismus-fif')
        self.failUnlessEqual(my_doc.meta_type, 'Naaya Document')
        self.failUnlessEqual(my_doc.title, unicode('Forschungsinstitut f\xc3\xbcr Freizeit und Tourismus (FIF)', 'utf-8'))
        self.failUnlessEqual(my_doc.body, 'This is a test document.')
        self.failUnlessEqual(my_doc.sortorder, 100)
        self.failUnless(my_doc.approved)        

    def test_import_bad_data(self):
        def do_import(row=''):
            self.portal.imported.csv_import.do_import(meta_type='Naaya URL',
                data=StringIO(csv_data+row))

        try:
            do_import('T,,,http://example.com\n')
        except:
            self.fail('Should not raise exception')

        self.failUnlessEqual(len(self.portal.imported.objectIds()), 3)
        self.failUnlessEqual(self.portal.imported._getOb('t').title, 'T')

        self.failUnlessRaises(ValueError, do_import, ',D,yes,http://example.com\n')
        self.failUnlessRaises(ValueError, do_import, 'T,D,asdf,http://example.com\n')

    def test_import_bad_metatype(self):
        def do_import():
            self.portal.imported.csv_import.do_import(meta_type='Nonexistent Metatype',
                data=StringIO(csv_data))
        self.failUnlessRaises(ValueError, do_import)

    def test_import_bad_destination(self):
        # TODO
        pass

class GeopointImportTest(NaayaTestCase):
    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'imported', contributor='contributor', submitted=1)
        schema = self.portal.portal_schemas.NyDocument
        schema.addWidget('test_geo_loc', label="Geo Loc", widget_type='Geo', data_type='geo')
        schema.addWidget('test_geo_type', label="Geo Type", widget_type='GeoType', data_type='str')
        self.portal.portal_map.addSymbol('sym1', 'Test symbol one', '', '', '', '')
        self.portal.portal_map.addSymbol('sym2', 'Test symbol two', '', '', '', '')

    def beforeTearDown(self):
        self.portal.portal_map.deleteSymbol(['sym1', 'sym2'])
        self.portal.portal_schemas.NyDocument.manage_delObjects('test_geo_loc-property')
        self.portal.portal_schemas.NyDocument.manage_delObjects('test_geo_type-property')
        self.portal.manage_delObjects(['imported'])

    def test_template(self):
        columns = self.portal.csv_import.template('Naaya Document').strip().split(',')
        self.failUnless('Geo Loc - lat' in columns)
        self.failUnless('Geo Loc - lon' in columns)
        self.failUnless('Geo Loc - address' in columns)
        self.failUnless('Geo Type' in columns)

    def test_import(self):
        geo_csv_data = (
            "Title,Geo Loc - lat,Geo Loc - lon,Geo Loc - address,Geo Type\n"
            "doc_one,,,,\n"
            "doc_two,13.45,22.60,,Test symbol one\n"
            "doc_three,8,9,somewhere else,Test symbol two\n"
            "doc_four,,,Bucharest,Test symbol two\n"
        )
        try:
            self.portal.imported.csv_import.do_import(meta_type='Naaya Document',
                data=StringIO(geo_csv_data))
        except:
            raise
            self.fail('Should not raise exception')
        self.failUnlessEqual(len(self.portal.imported.objectIds()), 4)

        doc_one = self.portal.imported._getOb('docone')
        self.failUnlessEqual(doc_one.title, 'doc_one')
        self.failIf(hasattr(doc_one, 'test_geo_loc'))
        self.failIf(hasattr(doc_one, 'test_geo_type'))

        doc_two = self.portal.imported._getOb('doctwo')
        self.failUnlessEqual(doc_two.test_geo_loc, Geo('13.45', '22.60'))
        self.failUnlessEqual(doc_two.test_geo_type, 'sym1')

        doc_three = self.portal.imported._getOb('docthree')
        self.failUnlessEqual(doc_three.test_geo_loc, Geo('8', '9', 'somewhere else'))
        self.failUnlessEqual(doc_three.test_geo_type, 'sym2')

        doc_four = self.portal.imported._getOb('docfour')
        self.failUnlessEqual(doc_four.test_geo_loc, Geo('44.434200', '26.102975', 'Bucharest'))
        self.failUnlessEqual(doc_four.test_geo_type, 'sym2')

class SecurityTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        pass

    def beforeTearDown(self):
        pass

    def test_anonymous(self):
        self.browser.go('http://localhost/portal/info/csv_import')
        self.assertTrue(self.browser.get_url().startswith(
            'http://localhost/portal/login_html'))

        self.browser.go('http://localhost/portal/csv_export/export_json')
        self.assertFalse(self.browser.get_html().startswith('{'))
        self.assertTrue(self.browser.get_url().startswith(
            'http://localhost/portal/login_html'))

    def test_admin(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/info/csv_import')
        self.assertEqual(self.browser.get_url(),
            'http://localhost/portal/info/csv_import')

        self.browser.go('http://localhost/portal/csv_export/export_json')
        self.assertTrue(self.browser.get_html().startswith('{'))

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyCSVImportTest))
    suite.addTest(makeSuite(GeopointImportTest))
    suite.addTest(makeSuite(SecurityTestCase))
    return suite
