from unittest import TestSuite, makeSuite
from Products.Naaya.tests import NaayaTestCase


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
