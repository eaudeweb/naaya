import json
from unittest import mock

import transaction
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
from naaya.content.url.url_item import addNyURL

from destinet.listing import listing
from destinet.testing.DestinetTestCase import DestinetFunctionalTestCase

SITE_URL = 'http://localhost/demo-design'


class ListingTest(DestinetFunctionalTestCase):

    def setUp(self):
        super(ListingTest, self).setUp()
        self.add_manager()
        catalog = self.portal.getCatalogTool()
        catalog.addIndex('topics', 'KeywordIndex')
        catalog.addIndex('target-groups', 'KeywordIndex')
        ptool = self.portal.getPortletsTool()
        manage_addRefList(ptool, 'target-groups', 'Target groups')
        ptool['target-groups'].manage_add_item('tourists', 'Tourists')
        ptool['target-groups'].manage_add_item('operators', 'Operators')
        resources = self.portal.resources
        addNyURL(resources, id='u1', title='"Zebra" crossing',
                 url='http://a.example.com', topics=['atopic'],
                 coverage='Romania', contributor='manager',
                 **{'target-groups': ['tourists', 'operators']})
        addNyURL(resources, id='u2', title='École verte',
                 url='http://b.example.com', topics=['other'],
                 coverage='France, ', contributor='manager',
                 **{'target-groups': ['operators']})
        addNyURL(resources, id='u3', title='apple',
                 url='http://c.example.com', contributor='manager')
        transaction.commit()

    def get_json(self, query):
        if 'length=' not in query:
            query += '&length=10'
        self.browser.go(SITE_URL + '/get_content?draw=7&' + query)
        self.assertEqual(self.browser.get_code(), 200)
        return json.loads(self.browser.result.text)

    def titles(self, data):
        return [row['name']['title'] for row in data['data']]

    def test_get_content_all(self):
        data = self.get_json('start=0&order[0][dir]=desc')
        self.assertEqual(data['draw'], 7)
        self.assertEqual(data['recordsTotal'], 3)
        self.assertEqual(data['recordsFiltered'], 3)
        self.assertEqual(self.titles(data),
                         ['apple', 'École verte', '"Zebra" crossing'])
        row = data['data'][1]
        self.assertEqual(row['name']['url'], SITE_URL + '/resources/u2')
        self.assertEqual(row['name']['translated'], {'id': '', 'title': ''})
        self.assertEqual(row['meta_type'], 'URL')
        self.assertEqual(row['coverage'], 'France')
        self.assertNotIn('target-groups', row)

    def test_get_content_order_asc_reverses(self):
        data = self.get_json('start=0&order[0][dir]=asc')
        self.assertEqual(self.titles(data),
                         ['"Zebra" crossing', 'École verte', 'apple'])

    def test_get_content_paging(self):
        data = self.get_json('start=1&length=1')
        self.assertEqual(data['recordsFiltered'], 3)
        self.assertEqual(self.titles(data), ['École verte'])

    def test_get_content_search(self):
        data = self.get_json('start=0&search[value]=%20Zebra%20')
        self.assertEqual(data['recordsTotal'], 3)
        self.assertEqual(data['recordsFiltered'], 1)
        self.assertEqual(self.titles(data), ['"Zebra" crossing'])

    def test_get_content_topic(self):
        data = self.get_json('start=0&topic=atopic')
        self.assertEqual(self.titles(data), ['"Zebra" crossing'])
        data = self.get_json('start=0&topic=atopic&topic=other')
        self.assertEqual(data['recordsTotal'], 2)

    def test_get_content_meta_type(self):
        data = self.get_json('start=0&columns[0][search][value]=News%20Item')
        self.assertEqual(data['data'], [])
        data = self.get_json('start=0&columns[0][search][value]=URL')
        self.assertEqual(data['recordsTotal'], 3)
        data = self.get_json('start=0&meta_type=Naaya%20News')
        self.assertEqual(data['recordsTotal'], 0)

    def test_get_content_target_groups(self):
        data = self.get_json('start=0&target_groups=all')
        self.assertEqual(self.titles(data),
                         ['École verte', '"Zebra" crossing'])
        self.assertEqual(data['data'][0]['target-groups'], 'Operators')
        self.assertEqual(data['data'][1]['target-groups'],
                         'Tourists, Operators')
        data = self.get_json('start=0&columns[3][search][value]=tourists')
        self.assertEqual(self.titles(data), ['"Zebra" crossing'])

    def test_get_content_translated_title(self):
        self.portal.gl_add_site_language('fr', 'French')
        self.portal._setLocalPropValue('title', 'en', 'Destinet')
        ob = self.portal.resources.u3
        ob._setLocalPropValue('title', 'en', '')
        ob._setLocalPropValue('title', 'fr', 'Pomme')
        ob._setLocalPropValue('coverage', 'fr', 'France')
        ob.recatalogNyObject(ob)
        transaction.commit()
        data = self.get_json('start=0&order[0][dir]=desc')
        row = [r for r in data['data'] if r['name']['url'].endswith('/u3')][0]
        self.assertEqual(row['name']['title'], 'u3')
        self.assertEqual(row['name']['translated'],
                         {'id': 'fr', 'title': 'French'})
        self.assertEqual(row['coverage'], 'France')

    def test_get_object_types(self):
        types = listing.get_object_types(self.portal, None)
        self.assertEqual(types, list(listing.RESOURCE_FRIENDLY_NAMES))
        self.browser.go(SITE_URL + '/get_object_types')
        self.assertEqual(self.browser.result.text, str(types))

    def test_get_keywords(self):
        ptool = self.portal.getPortletsTool()
        manage_addRefList(ptool, 'certificate_keywords', 'Keywords')
        reflist = ptool.getRefListById('certificate_keywords')
        self.assertIsNotNone(reflist)
        reflist.manage_add_item('zero', 'Zero waste')
        reflist.manage_add_item('alpha', 'Alpha')
        reflist.manage_add_item('beta', 'Beta')
        self.assertEqual(listing.get_keywords(self.portal, None), [
            ('alpha', 'Alpha'), ('beta', 'Beta'), ('zero', 'Zero waste')])

    def test_second_level(self):
        addNyFolder(self.portal, 'hidden', title='Hidden', keywords='nomenu')
        addNyFolder(self.portal, 'visible', title='Visible',
                    keywords='other')
        for ob_id in ('hidden', 'visible'):
            self.portal[ob_id].approveThis()
        with mock.patch.dict('os.environ',
                             {'DESTINET_NAVIGATION_KEYWORD': 'nomenu'}):
            ids = [ob.getId()
                   for ob in listing.second_level(self.portal, None)]
        self.assertIn('visible', ids)
        self.assertNotIn('hidden', ids)
        self.assertNotIn('resources', ids)

    def test_change_to_english(self):
        client = self.browser._twill._client
        response = client.get(SITE_URL + '/change_to_english')
        self.assertEqual(response.headers.get('set-cookie'),
                         'LOCALIZER_LANGUAGE=en; Path=/')
        client.cookies.set('LOCALIZER_LANGUAGE', 'fr')
        response = client.get(SITE_URL + '/change_to_english')
        self.assertIsNone(response.headers.get('set-cookie'))
