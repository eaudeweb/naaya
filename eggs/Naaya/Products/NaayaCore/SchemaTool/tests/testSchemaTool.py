from unittest import TestSuite, TestLoader
from Products.Naaya.tests import NaayaTestCase


class NaayaSchemaToolTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Schema Tool """

    def test_tool_in_new_site(self):
        """ make sure the SchemaTool is instantiated in a new NySite """
        self.assertTrue('portal_schemas' in self.portal.objectIds())
        self.assertEqual(self.portal.portal_schemas.title, 'Portal schemas')

        initial_schemas = set(self.portal.portal_schemas.objectIds())
        expected_schemas = set(['NyDocument', 'NyEvent', 'NyExFile', 'NyFile',
                'NyGeoPoint', 'NyMediaFile', 'NyNews', 'NyPointer', 'NyStory', 'NyURL'])
        self.assertTrue(expected_schemas.issubset(initial_schemas))

    def test_getSchemaForMetatype(self):
        tool = self.portal.portal_schemas
        self.assertEqual(tool.NyDocument, tool.getSchemaForMetatype('Naaya Document'))
        self.assertEqual(tool.getSchemaForMetatype('No Such Type'), None)

    def test_listSchemas(self):
        schemas = self.portal.portal_schemas.listSchemas()
        self.assertTrue('Naaya Document' in schemas.keys())
        self.assertTrue(schemas['Naaya Document'].absolute_url()
            == self.portal.portal_schemas.NyDocument.absolute_url())
