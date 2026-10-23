from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.GeoMapTool.tests.test_kml_parser import load_file
from Products.NaayaCore.PortletsTool.RefList import manage_addRefList

from naaya.content.certificate.certificate_item import importNyCertificate


class CertificateTest(NaayaTestCase):

    def afterSetUp(self):
        map_tool = self.portal.getGeoMapTool()
        picture = load_file('data/symbol.png')
        map_tool.addSymbol('market', 'MARKET PLACE', '', '', None, picture, '')
        map_tool.addSymbol('hotel', 'Hotel', '', 'market', None, picture, '')
        self.portal.manage_install_pluggableitem('Naaya Certificate')
        ptool = self.portal.getPortletsTool()
        manage_addRefList(ptool, 'topics', 'Topics')
        ptool.topics.manage_add_item('atopic', 'A topic')
        self.portal.portal_schemas['NyContact'].addWidget(
            'topics', widget_type='SelectMultiple', data_type='list',
            list_id='topics')
        addNyFolder(self.portal, 'certs', contributor='admin', submitted=1)
        self.login()

    def beforeTearDown(self):
        self.logout()

    def import_certificate(self):
        attrs = {'contributor': 'admin', 'sortorder': '100',
                 'discussion': '0', 'organisation': 'Green Keys',
                 'phone': '+40 1', 'fax': '', 'cellphone': '',
                 'email': 'info@example.com', 'webpage': 'http://example.com',
                 'approved': '1', 'approved_by': 'admin',
                 'releasedate': '30/04/2020'}
        properties = {'title': {'en': 'Green Key ș'},
                      'description': {'en': '<p>Eco label</p>'},
                      'coverage': {'en': 'Romania'}}
        importNyCertificate(self.portal.certs, 0, 'gk', attrs, '', properties,
                            None, None)
        return self.portal.certs.gk

    def test_install(self):
        ptool = self.portal.getPortletsTool()
        self.assertEqual([n.id for n in ptool.certificate_categories
                          .objectValues()], ['hotel'])

    def test_import(self):
        ob = self.import_certificate()
        self.assertEqual(ob.getLocalProperty('title', 'en'), 'Green Key ș')
        self.assertIsInstance(ob.getLocalProperty('description', 'en'), str)
        self.assertEqual(ob.organisation, 'Green Keys')
        self.assertEqual(ob.email, 'info@example.com')
        self.assertEqual(ob.approved, 1)
        self.assertEqual(ob.releasedate.year(), 2020)
        catalog = self.portal.getCatalogTool()
        self.assertEqual([b.id for b in catalog(meta_type='Naaya Certificate')],
                         ['gk'])

    def test_index_unknown_topic(self):
        ob = self.import_certificate()
        ob.topics = ['atopic', 'removed-topic']
        html = ob.index_html(self.portal.REQUEST)
        self.assertIn('Green Key ș', html)
        self.assertIn('A topic', html)
        self.assertIn('removed-topic', html)
