from io import BytesIO

from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.PortletsTool.RefList import manage_addRefList

from naaya.content.goodpracticebusiness.goodpracticebusiness_item import (
    addNyGoodPracticeBusiness)

REQUIRED = {
    'description': 'A good business',
    'coverage': 'Romania',
    'geo_location.lat': '45.5',
    'geo_location.lon': '25.5',
    'gstc_industry': ['ind1'],
    'landscape_type': 'coast',
    'topics': ['atopic'],
    'category': 'hotel',
}


def upload(name, data=b'%PDF-1.4 test'):
    f = BytesIO(data)
    f.filename = name
    f.headers = {'content-type': 'application/pdf'}
    return f


class GoodPracticeBusinessTest(NaayaTestCase):

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Good Practice Business')
        ptool = self.portal.getPortletsTool()
        for list_id, item_id, title in [('landscape_type', 'coast', 'Coast'),
                                        ('topics', 'atopic', 'A topic'),
                                        ('gstc_industry', 'ind1',
                                         'Industry criterion'),
                                        ('certificate_categories', 'hotel',
                                         'Hotel')]:
            if list_id not in ptool.objectIds():
                manage_addRefList(ptool, list_id, list_id)
            ptool[list_id].manage_add_item(item_id, title)
        addNyFolder(self.portal, 'market', contributor='admin', submitted=1)
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_add_with_file_and_no_title(self):
        folder = self.portal.market
        ob_id = addNyGoodPracticeBusiness(
            folder, uploaded_file=upload('Green hotel.pdf'),
            contributor='admin', **REQUIRED)
        ob = folder[ob_id]
        self.assertEqual(ob.title, 'Green hotel')
        version = ob.current_version
        self.assertIsNotNone(version)
        self.assertEqual(version.filename, 'Green hotel.pdf')
        self.assertEqual(version.contributor, 'admin')
        html = ob.index_html(self.portal.REQUEST)
        self.assertIn('Green hotel', html)
        self.assertIn('Industry criterion', html)

    def test_add_without_file_or_title(self):
        self.assertRaises(ValueError, addNyGoodPracticeBusiness,
                          self.portal.market, **REQUIRED)
