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
        self.objs = [info, info.accessibility, info.cookie_policy, info.contact]
        for i in range(10):
            rd = '%2d/01/2100' % (i+1)
            new_folder = info[addNyFolder(info, 'test%d' % i, releasedate=rd)]
            new_folder.approveThis(1, '')
            self.objs.insert(0, new_folder)
            self.portal.recatalogNyObject(new_folder)
        # and one unapproved in the middle
        addNyFolder(info, 'test10', releasedate='09/01/2011')

    def test_getCatalogedObjectsCheckView_all(self):
        all_in_cat = self.portal.getCatalogedObjectsCheckView(approved=1)
        self.assertEqual(all_in_cat, self.objs)

    def test_getCatalogedObjectsCheckView_limit(self):
        latest_3 = self.portal.getCatalogedObjectsCheckView(howmany=3, approved=1)
        self.assertEqual(latest_3, self.objs[:3])

    def test_getCatalogedObjectsCheckView_overflow_limit(self):
        latest_30 = self.portal.getCatalogedObjectsCheckView(howmany=30, approved=1)
        self.assertEqual(latest_30, self.objs)

    def test_latest_visible_uploads(self):
        latest = []
        for x in self.portal.latest_visible_uploads():
            latest.append(x)
        self.assertEqual(latest, self.objs)
