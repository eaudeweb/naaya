from unittest import TestSuite, makeSuite

from zope import interface
from OFS.SimpleItem import SimpleItem

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.CatalogTool.interfaces import INyCatalogAware
from naaya.content.url.url_item import NyURL, addNyURL

class BasicObject(SimpleItem):
    meta_type = 'Basic Test Object'

class CatalogAwareObject(BasicObject):
    meta_type = 'Catalog Aware Test Object'
    interface.implements(INyCatalogAware)

class CatalogAwarenessTest(NaayaTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfol',
                    contributor='contributor', submitted=1)

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfol'])

    def search(self, meta_type):
        catalog = self.portal.getCatalogTool()
        brains = catalog(meta_type=meta_type)
        return [b.getObject() for b in brains]

    def test_basic_object(self):
        myfol = self.portal['myfol']
        self.assertEqual(len(self.search(BasicObject.meta_type)), 0)

        myfol._setObject('ob', BasicObject('ob'))
        self.assertEqual(len(self.search(BasicObject.meta_type)), 0)

        myfol.manage_delObjects(['ob'])
        self.assertEqual(len(self.search(BasicObject.meta_type)), 0)

    def test_catalog_aware_object(self):
        myfol = self.portal['myfol']
        self.assertEqual(len(self.search(CatalogAwareObject.meta_type)), 0)

        myfol._setObject('ob', CatalogAwareObject('ob'))
        self.assertEqual(len(self.search(CatalogAwareObject.meta_type)), 1)

        myfol.manage_delObjects(['ob'])
        self.assertEqual(len(self.search(CatalogAwareObject.meta_type)), 0)

    def test_nyurl(self):
        myfol = self.portal['myfol']
        self.assertEqual(len(self.search(NyURL.meta_type)), 0)

        addNyURL(myfol, id='ob', title='Test URL')
        self.assertEqual(len(self.search(NyURL.meta_type)), 1)

        myfol.manage_delObjects(['ob'])
        self.assertEqual(len(self.search(NyURL.meta_type)), 0)
