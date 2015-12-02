from unittest import TestSuite, makeSuite
from StringIO import StringIO

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.content.contact.contact_item import addNyContact

from Products.NaayaCore.GeoMapTool.tests.test_kml_parser import load_file

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


class GeopointExportTest(NaayaTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'toexport',
                    contributor='contributor', submitted=1)
        schema = self.portal.portal_schemas.NyContact
        schema.addWidget('test_geo_loc', label="Geo Loc",
                         widget_type='Geo', data_type='geo')
        schema.addWidget('test_geo_type', label="Geo Type",
                         widget_type='GeoType', data_type='str')

        picture_data = load_file('data/symbol.png')
        self.portal.portal_map.addSymbol('sym1', 'Test symbol one',
                                         '', '', None, picture_data, '')

    def beforeTearDown(self):
        nycontact_schema = self.portal['portal_schemas']['NyContact']
        nycontact_schema.manage_delObjects('test_geo_loc-property')
        nycontact_schema.manage_delObjects('test_geo_type-property')
        self.portal.portal_map.deleteSymbol(['sym1'])
        self.portal.manage_delObjects(['toexport'])

    def test_export_geolocation(self):
        toexport = self.portal['toexport']
        addNyContact(toexport, id='contact1', title='Contact 1',
                     contributor='contributor')
        toexport['contact1'].test_geo_loc = Geo('13.45', '22.60', 'somewhere')

        csv_output = toexport.csv_export.export(meta_type='Naaya Contact')
        csv_lines = csv_output.strip().split('\n')
        self.assertEqual(len(csv_lines), 2) # header line and one object
        csv_data = dict(zip(*(line.split(',') for line in csv_lines)))
        self.assertEqual(csv_data['Geo Loc - lat'], '13.45')
        self.assertEqual(csv_data['Geo Loc - lon'], '22.60')
        self.assertEqual(csv_data['Geo Loc - address'], 'somewhere')

    def test_export_geotype(self):
        toexport = self.portal['toexport']
        addNyContact(toexport, id='contact1', title='Contact 1',
                     contributor='contributor')
        toexport['contact1'].test_geo_type = 'sym1'

        csv_output = toexport.csv_export.export(meta_type='Naaya Contact')
        csv_lines = csv_output.strip().split('\n')
        self.assertEqual(len(csv_lines), 2) # header line and one object
        csv_data = dict(zip(*(line.split(',') for line in csv_lines)))
        self.assertEqual(csv_data['Geo Type'], 'Test symbol one')
