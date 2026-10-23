"""Log in through the login form and work with content through the web forms of a destinet site."""
import io
import json

import transaction

from destinet.testing.DestinetTestCase import DestinetFunctionalTestCase

SITE_URL = 'http://localhost/demo-design'
FOLDER_URL = SITE_URL + '/resources/e2e-folder'
WORD = 'Zirconflax'  # a word no other content contains, for the search


class EndToEndTest(DestinetFunctionalTestCase):

    def setUp(self):
        super(EndToEndTest, self).setUp()
        self.add_manager('editor', 'editor-pw')
        self.portal.portal_map.addSymbol('hotel', 'Hotel', '', '', '#ff0000', None, '')
        transaction.commit()

    def submit(self, url, form_name, values, files=None):
        self.browser.go(url)
        self.assertEqual(self.browser.get_code(), 200, url)
        form = self.browser.get_form(form_name)
        self.browser.clicked(form, self.browser.get_form_field(form, list(values)[0]))
        for name, value in values.items():
            form[name] = value
        for name, (data, filename) in (files or {}).items():
            form.find_control(name).add_file(io.BytesIO(data), 'text/plain', filename)
        self.browser.submit()
        self.assertEqual(self.browser.get_code(), 200, self.browser.get_url())
        return self.browser.get_html()

    def login(self, user, password):
        self.submit(SITE_URL + '/login_html', 'signin',
                    {'__ac_name': user, '__ac_password': password})

    def test_content_through_the_web(self):
        self.login('editor', 'editor-pw')
        self.browser.go(SITE_URL)
        self.assertIn('logout', self.browser.get_html().lower())

        self.submit(SITE_URL + '/resources/folder_add_html', 'frmAdd',
                    {'title:utf8:string': 'E2E folder'})
        self.assertIn('e2e-folder', self.portal.resources.objectIds())

        self.submit(FOLDER_URL + '/news_add_html', 'frmAdd',
                    {'title:utf8:string': 'Știri %s' % WORD,
                     'description:utf8:string': 'Descriere cu diacritice'})
        news_id = self.portal.resources['e2e-folder'].objectIds(['Naaya News'])[0]
        self.submit(FOLDER_URL + '/%s/edit_html' % news_id, 'frmEdit',
                    {'title:utf8:string': 'Știri editate %s' % WORD})
        self.assertEqual(self.portal.resources['e2e-folder'][news_id].title,
                         'Știri editate %s' % WORD)

        self.submit(FOLDER_URL + '/bfile_add_html', 'frmAdd',
                    {'title:utf8:string': 'Fișier'},
                    files={'uploaded_file': (b'file content \xc8\x99', 'fișier.txt')})
        bfile = self.portal.resources['e2e-folder'].objectValues(['Naaya Blob File'])[0]
        self.browser.go('%s/%s/download' % (FOLDER_URL, bfile.getId()))
        self.assertEqual(self.browser.result.content, b'file content \xc8\x99')

        self.submit(FOLDER_URL + '/geopoint_add_html', 'frmAdd',
                    {'title:utf8:string': 'Punct %s' % WORD, 'geo_type:utf8:string': 'hotel',
                     'geo_location.lat:utf8:string': '45.65',
                     'geo_location.lon:utf8:string': '25.6',
                     'geo_location.address:utf8:string': 'Brașov'})

        self.browser.go(SITE_URL + '/search_html?query=' + WORD)
        html = self.browser.get_html()
        self.assertIn('Știri editate %s' % WORD, html)
        self.assertIn('Punct %s' % WORD, html)

        self.browser.go(SITE_URL + '/portal_map/xrjs_getGeoClusters?lat_min=40&lat_max=50'
                        '&lon_min=20&lon_max=30&geo_types:list=hotel&geo_query=')
        points = json.loads(self.browser.get_html())['points']
        self.assertIn('Punct %s' % WORD, [p['label'] for p in points])

        # the Delete button of the folder listing
        self.browser.go(SITE_URL + '/resources/')
        form = self.browser.get_form('objectItems')
        form['id'] = ['e2e-folder']
        self.browser.clicked(form, self.browser.get_form_field(form, 'deleteObjects:method'))
        self.browser.submit()
        self.assertEqual(self.browser.get_code(), 200)
        self.assertNotIn('e2e-folder', self.portal.resources.objectIds())
