from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder

class CatalogToolTestSuite(NaayaTestCase):
    """
    Testing catalog_tool mixing class in
    :mod:`Products.NaayaCore.managers.catalog_tool`

    """
    def setUp(self):
         super(CatalogToolTestSuite, self).setUp()
         info = self.portal.info
         self.objs = [info, info.accessibility, info.contact]
         for i in range(10):
             rd = '%2d/01/2100' % i
             self.objs.insert(0, info[addNyFolder(info, 'test%d' % i,
                                                  releasedate=rd)])

    def test_getCatalogedObjectsCheckView_all(self):
         all_in_cat = self.portal.getCatalogedObjectsCheckView()
         self.assertEqual(all_in_cat, self.objs)

    def test_getCatalogedObjectsCheckView_limit(self):
         latest_3 = self.portal.getCatalogedObjectsCheckView(howmany=3)
         self.assertEqual(latest_3, self.objs[:3])

    def test_getCatalogedObjectsCheckView_overflow_limit(self):
         latest_30 = self.portal.getCatalogedObjectsCheckView(howmany=30)
         self.assertEqual(latest_30, self.objs)

