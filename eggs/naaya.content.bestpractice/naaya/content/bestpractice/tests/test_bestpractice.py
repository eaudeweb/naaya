from io import BytesIO

import transaction
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.PortletsTool.RefList import manage_addRefList

from naaya.content.bestpractice.bestpractice_item import addNyBestPractice

REQUIRED = {
    'description': 'A good practice',
    'coverage': 'Romania',
    'geo_location.lat': '45.5',
    'geo_location.lon': '25.5',
    'gstc_criteria': ['GSTCDA1'],
    'landscape_type': 'coast',
    'topics': ['atopic'],
    'category': 'hotel',
}


def upload(name, data=b'%PDF-1.4 test'):
    f = BytesIO(data)
    f.filename = name
    f.headers = {'content-type': 'application/pdf'}
    return f


class BestPracticeTest(NaayaTestCase):

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Best Practice')
        ptool = self.portal.getPortletsTool()
        for list_id, item_id, title in [('landscape_type', 'coast', 'Coast'),
                                        ('topics', 'atopic', 'A topic'),
                                        ('certificate_categories', 'hotel',
                                         'Hotel')]:
            if list_id not in ptool.objectIds():
                manage_addRefList(ptool, list_id, list_id)
            ptool[list_id].manage_add_item(item_id, title)
        addNyFolder(self.portal, 'topics', contributor='admin', submitted=1)
        self.login()

    def beforeTearDown(self):
        self.logout()
        self.portal.manage_delObjects(['topics'])
        self.portal.manage_uninstall_pluggableitem('Naaya Best Practice')
        transaction.commit()

    def test_add_with_file_and_no_title(self):
        folder = self.portal.topics
        ob_id = addNyBestPractice(folder, uploaded_file=upload('Eco guide.pdf'),
                                  contributor='admin', **REQUIRED)
        ob = folder[ob_id]
        self.assertEqual(ob.title, 'Eco guide')
        self.assertEqual(ob.gstc_criteria, ['GSTCDA1'])
        version = ob.current_version
        self.assertIsNotNone(version)
        self.assertEqual(version.filename, 'Eco guide.pdf')
        self.assertEqual(version.contributor, 'admin')
        self.assertEqual(ob.current_version_download_url(),
                         ob.absolute_url() + '/download/en/1/Eco%20guide.pdf')
        html = ob.index_html(self.portal.REQUEST)
        self.assertIn('Eco guide', html)
        self.assertIn('A good practice', html)
        self.assertIn('Coast', html)
        self.assertIn('A.1. Sustainable destination strategy', html)

    def test_add_requires_criteria(self):
        data = dict(REQUIRED, gstc_criteria=[])
        self.assertRaises(ValueError, addNyBestPractice, self.portal.topics,
                          title='No criteria', **data)

    def test_install_creates_reftree_and_index(self):
        self.assertIn('gstc_criteria', self.portal.getPortletsTool().objectIds())
        self.assertIn('gstc_criteria', self.portal.getCatalogTool().indexes())
