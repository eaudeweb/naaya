import datetime
from hashlib import md5

import transaction
from lxml import etree
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.GeoMapTool.tests.test_kml_parser import load_file
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.content.contact.contact_item import addNyContact
from naaya.content.url.url_item import addNyURL

from destinet.syndication.syndication import (display_date,
                                              index_rdf_extended,
                                              syndicateThisExtended)
from destinet.testing.DestinetTestCase import DestinetFunctionalTestCase

NS = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
      'dc': 'http://purl.org/dc/elements/1.1/',
      'rss': 'http://purl.org/rss/1.0/'}
SECTION = 'who-who/market-place/certifiers-section'


class SyndicationTest(DestinetFunctionalTestCase):

    def setUp(self):
        super(SyndicationTest, self).setUp()
        self.add_manager()
        self.portal.portal_map.addSymbol('certifier', 'Certifier', '', '',
                                         None, load_file('data/symbol.png'),
                                         '')
        addNyFolder(self.portal['who-who'], 'market-place')
        addNyFolder(self.portal['who-who']['market-place'],
                    'certifiers-section', title='Certifiers')
        self.section = self.portal.unrestrictedTraverse(SECTION)
        addNyContact(self.section, id='c1', title='Green Certifier ș',
                     description='<p>Certifies things</p>',
                     geo_location=Geo('45.5', '25.5', 'Brașov, Romania'),
                     webpage='http://cert.example.com',
                     coverage='Romania, Bulgaria',
                     **{'category-organization': 'certifier',
                        'category-marketplace': 'certifier'})
        contact = self.section.c1
        contact.expiry_date = datetime.date(2030, 3, 5)
        contact.id_number = 1234
        addNyURL(self.section, id='link', title='A link',
                 url='http://example.com', contributor='manager')
        transaction.commit()

    def go(self, path):
        self.browser.go('http://localhost/demo-design/' + path)
        return self.browser.result.text

    def parse(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return etree.fromstring(data)

    def check_contact_item(self, item):
        def field(name):
            return item.findtext('dc:' + name, namespaces=NS)
        self.assertEqual(item.get('{%s}about' % NS['rdf']),
                         'http://localhost/demo-design/%s/c1' % SECTION)
        self.assertEqual(field('title'), 'Green Certifier ș')
        self.assertEqual(field('description'), '<p>Certifies things</p>')
        self.assertEqual(field('address'), 'Brașov, Romania')
        self.assertEqual(field('webpage'), 'http://cert.example.com')
        self.assertEqual(field('lat'), '45.5')
        self.assertEqual(field('lon'), '25.5')
        self.assertEqual(field('marketplace_category'), 'Certifier')
        self.assertEqual(field('expiry_date'), '05 March 2030')
        self.assertEqual(field('id_number'), '1234')
        self.assertEqual([c.text for c in item.findall('dc:country', NS)],
                         ['Romania', 'Bulgaria'])

    def test_syndicate_contact_returns_text(self):
        out = syndicateThisExtended(self.section.c1)
        self.assertIsInstance(out, str)
        self.check_contact_item(self.parse(
            '<rdf:RDF xmlns:rdf="%(rdf)s" xmlns:dc="%(dc)s">%%s</rdf:RDF>'
            % NS % out)[0])

    def test_syndicate_other_type_uses_default(self):
        out = syndicateThisExtended(self.section.link)
        self.assertIsInstance(out, str)
        self.assertIn('A link', out)

    def test_folder_feed(self):
        self.browser_basic_auth()
        text = self.go(SECTION + '/index_rdf_extended')
        self.assertEqual(self.browser.get_code(), 200)
        self.assertTrue(
            self.browser_get_header('content-type').startswith('text/xml'))
        xml = self.parse(text)
        channel = xml.find('rss:channel', NS)
        self.assertEqual(channel.findtext('rss:link', namespaces=NS),
                         'http://localhost/demo-design/' + SECTION)
        seq = [li.get('resource')
               for li in channel.findall('rss:items/rdf:Seq/rdf:li', NS)]
        self.assertEqual(sorted(seq), [
            'http://localhost/demo-design/%s/c1' % SECTION,
            'http://localhost/demo-design/%s/link' % SECTION])
        items = {i.get('{%s}about' % NS['rdf']).rsplit('/', 1)[1]: i
                 for i in xml.findall('rss:item', NS)}
        self.assertEqual(sorted(items), ['c1', 'link'])
        self.check_contact_item(items['c1'])
        received = ''.join(syndicateThisExtended(ob) for ob in
                           self.section.getPublishedContent())
        self.assertEqual(channel.findtext('dc:hash', namespaces=NS),
                         md5(received.encode('utf-8')).hexdigest())

    def test_contact_feed(self):
        out = index_rdf_extended(self.section.c1, self.portal.REQUEST)
        self.assertIsInstance(out, bytes)
        xml = self.parse(out)
        items = xml.findall('rss:item', NS)
        self.assertEqual(len(items), 1)
        self.check_contact_item(items[0])

    def test_feed_requires_permission(self):
        self.go(SECTION + '/index_rdf_extended')
        self.assertIn('/login_html', self.browser.get_url())

    def test_redirect_outside_certifiers_section(self):
        self.browser_basic_auth()
        self.go('resources/index_rdf_extended')
        self.assertEqual(self.browser.get_url(),
                         'http://localhost/demo-design/resources/index_rdf')

    def test_display_date(self):
        self.assertEqual(display_date(None), '')
        self.assertEqual(display_date(''), '')
        self.assertEqual(display_date(datetime.date(2020, 1, 2)),
                         '02 January 2020')
