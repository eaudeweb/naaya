import transaction
from zope.component import getMultiAdapter
from zope.publisher.browser import setDefaultSkin
from naaya.content.url.url_item import addNyURL

from destinet.testing.DestinetTestCase import DestinetFunctionalTestCase

FOLDER_URL = 'http://localhost/demo-design/resources'


class KeywordsTest(DestinetFunctionalTestCase):

    def setUp(self):
        super(KeywordsTest, self).setUp()
        self.add_manager()
        resources = self.portal.resources
        addNyURL(resources, id='u1', title='First', url='http://a.example.com',
                 keywords='beta, alpha', contributor='manager')
        addNyURL(resources, id='u2', title='Second',
                 url='http://b.example.com', keywords='zeta',
                 contributor='manager')
        transaction.commit()
        self.browser_basic_auth()

    def post(self, data):
        response = self.browser._twill._client.post(
            FOLDER_URL + '/allocateKeywords', data=data,
            follow_redirects=False)
        transaction.begin()
        return response

    def keywords(self, ob_id):
        return self.portal.resources[ob_id].getLocalProperty('keywords',
                                                             'en')

    def form(self, bulk_keywords, bulk_action='allocate', checked=('u1',)):
        return {
            'redirect_url': FOLDER_URL,
            'lang': 'en',
            'bulk_action': bulk_action,
            'bulk_keywords:utf8:string': bulk_keywords,
            'checked_paths:list': ['/demo-design/resources/%s' % ob_id
                                   for ob_id in checked],
            'paths:list': ['/demo-design/resources/u1',
                           '/demo-design/resources/u2'],
            'keywords:utf8:string:list': [self.keywords('u1'),
                                          self.keywords('u2')],
        }

    def test_form_lists_selected_objects(self):
        self.browser.go(FOLDER_URL + '/allocate_keywords_html?id=u1&id=u2')
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertIn('action="%s/allocateKeywords"' % FOLDER_URL, html)
        self.assertIn('value="/demo-design/resources/u1"', html)
        self.assertIn('value="/demo-design/resources/u2"', html)
        self.assertIn('value="beta, alpha"', html)
        self.assertIn('value="zeta"', html)

    def test_form_single_id(self):
        request = self.portal.REQUEST
        setDefaultSkin(request)
        request.form['id'] = 'u2'
        view = getMultiAdapter((self.portal.resources, request),
                               name='allocate_keywords_html')
        html = view(request)
        self.assertIn('value="/demo-design/resources/u2"', html)
        self.assertNotIn('value="/demo-design/resources/u1"', html)

    def test_form_without_selection_redirects(self):
        self.browser.go(FOLDER_URL + '/allocate_keywords_html')
        self.assertEqual(self.browser.get_url(), FOLDER_URL)
        self.assertIn('No keywords were selected!', self.browser.get_html())

    def test_allocate_bulk_keywords(self):
        form = self.form('gamma, alpha, ')
        form['keywords:utf8:string:list'] = ['beta, alpha', 'zeta, eta']
        response = self.post(form)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['location'], FOLDER_URL)
        self.assertEqual(self.keywords('u1'), 'alpha, beta, gamma')
        self.assertEqual(self.keywords('u2'), 'eta, zeta')
        catalog = self.portal.getCatalogTool()
        found = [b.id for b in catalog(objectkeywords_en='gamma')]
        self.assertEqual(found, ['u1'])

    def test_remove_bulk_keywords(self):
        self.post(self.form('alpha, zeta, missing', 'remove',
                            checked=('u1', 'u2')))
        self.assertEqual(self.keywords('u1'), 'beta')
        self.assertEqual(self.keywords('u2'), '')

    def test_missing_bulk_action_redirects(self):
        form = self.form('gamma')
        del form['bulk_action']
        response = self.post(form)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['location'], FOLDER_URL)
        self.assertEqual(self.keywords('u1'), 'beta, alpha')
