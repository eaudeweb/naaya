import transaction
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.GeoMapTool.tests.test_kml_parser import load_file
from naaya.content.contact.contact_item import addNyContact
from naaya.content.url.url_item import addNyURL

from destinet.testing.DestinetTestCase import DestinetFunctionalTestCase

SITE_URL = 'http://localhost/demo-design'
PUBLISHER_URL = SITE_URL + '/destinet.publisher'


class PublisherTestSuite(DestinetFunctionalTestCase):

    def setUp(self):
        super(PublisherTestSuite, self).setUp()
        self.add_manager()
        map_tool = self.portal.portal_map
        for symbol_id, title in [('hotel', 'Hotel'), ('ngo', 'NGO'),
                                 ('green', 'Green & Clean')]:
            map_tool.addSymbol(symbol_id, title, '', '', None,
                               load_file('data/symbol.png'), '')
        who_who = self.portal['who-who']
        addNyFolder(who_who, 'market-place')
        addNyFolder(who_who['market-place'], 'hotel', title='Hotel')
        addNyFolder(who_who, 'ngo', title='NGO')
        addNyFolder(who_who, 'green-and-clean', title='Green and Clean')
        transaction.commit()
        self.browser_basic_auth()

    def post(self, method, data):
        response = self.browser._twill._client.post(
            PUBLISHER_URL + '/' + method, data=data, follow_redirects=False)
        transaction.begin()
        return response

    def contacts(self, folder):
        return folder.objectIds('Naaya Contact')

    def test_url_without_topic_or_target_group(self):
        response = self.post('addNyURL', {'title': 'Link',
                                          'locator': 'http://a.example.com'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/disseminate_url')
        self.assertEqual(self.portal.resources.objectIds('Naaya URL'), [])

    def test_url_created_in_resources(self):
        response = self.post('addNyURL', {'title': 'Link',
                                          'locator': 'http://a.example.com',
                                          'topics:list': 'atopic'})
        self.assertEqual(response.headers['location'],
                         SITE_URL + '/resources/link')
        ob = self.portal.resources.link
        self.assertEqual(ob.locator, 'http://a.example.com')
        self.assertEqual(ob.topics, ['atopic'])

    def test_event_created_in_events(self):
        response = self.post('addNyEvent', {
            'title': 'Fair', 'start_date': '10/10/2030',
            'target-groups:list': 'tourists'})
        self.assertEqual(response.headers['location'],
                         SITE_URL + '/events/fair')
        self.assertEqual(self.portal.events.fair.start_date.year(), 2030)

    def test_event_errors_back_to_form(self):
        response = self.post('addNyEvent', {'title': 'Fair',
                                            'topics:list': 'atopic'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/promote_event')
        self.assertEqual(self.portal.events.objectIds('Naaya Event'), [])
        response = self.post('addNyEvent', {'title': 'Fair',
                                            'start_date': '10/10/2030'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/promote_event')

    def test_news_created_in_news(self):
        response = self.post('addNyNews', {'title': 'Hello',
                                           'topics:list': 'atopic'})
        self.assertEqual(response.headers['location'],
                         SITE_URL + '/News/hello')
        response = self.post('addNyNews', {'title': 'Other'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/promote_news')
        self.assertEqual(self.portal.News.objectIds('Naaya News'), ['hello'])

    def test_publication_disseminate_and_market(self):
        self.post('addNyPublication_disseminate', {
            'title': 'Guide', 'locator': 'http://g.example.com',
            'topics:list': 'atopic'})
        self.assertEqual(
            self.portal.resources.objectIds('Naaya Publication'), ['guide'])
        response = self.post('addNyPublication_market', {
            'title': 'Offer', 'locator': 'http://o.example.com'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/market_place_publication')
        self.post('addNyPublication_market', {
            'title': 'Offer', 'locator': 'http://o.example.com',
            'topics:list': 'atopic'})
        self.assertEqual(
            self.portal['market-place'].objectIds('Naaya Publication'),
            ['offer'])

    def test_contact_market(self):
        response = self.post('addNyContact_market', {
            'title': 'Shop', 'category-organization': 'hotel'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/market_place_contact')
        self.post('addNyContact_market', {
            'title': 'Shop', 'category-organization': 'hotel',
            'topics:list': 'atopic'})
        self.assertEqual(self.contacts(self.portal['market-place']), ['shop'])

    def test_contact_user_gets_destinet_user_keyword(self):
        response = self.post('addNyContact_user', {
            'title': 'Me', 'category-organization': 'ngo'})
        self.assertEqual(response.headers['location'],
                         PUBLISHER_URL + '/user_contact')
        self.post('addNyContact_user', {
            'title': 'Me', 'category-organization': 'ngo',
            'keywords': 'eco', 'topics:list': 'atopic'})
        users = self.portal['who-who']['destinet-users']
        self.assertEqual(self.contacts(users), ['me'])
        keywords = users.me.getLocalProperty('keywords', 'en').split(', ')
        self.assertEqual(sorted(keywords), ['Destinet User', 'eco'])
        self.assertEqual(users.me.geo_type, 'ngo')

    def test_contact_who_who_placed_by_category(self):
        who_who = self.portal['who-who']
        self.post('addNyContact_who_who', {
            'title': 'Org', 'category-organization': 'ngo',
            'topics:list': 'atopic'})
        self.assertEqual(self.contacts(who_who.ngo), ['org'])
        self.post('addNyContact_who_who', {
            'title': 'Inn', 'category-organization': 'ngo',
            'category-marketplace': 'hotel', 'topics:list': 'atopic'})
        inn = who_who['market-place'].hotel.inn
        self.assertEqual(inn.geo_type, 'hotel')
        self.post('addNyContact_who_who', {
            'title': 'Clean', 'category-organization': 'green',
            'topics:list': 'atopic'})
        self.assertEqual(self.contacts(who_who['green-and-clean']), ['clean'])
        self.post('addNyContact_who_who', {
            'title': 'Nowhere', 'category-organization': 'unknown',
            'topics:list': 'atopic'})
        self.assertEqual(self.contacts(who_who), ['nowhere'])

    def test_contact_who_who_een_group(self):
        self.post('addNyContact_who_who', {
            'title': 'Org', 'category-organization': 'ngo',
            'topics:list': 'atopic',
            'groups:list': 'european-ecotourism-network'})
        org = self.portal['who-who'].ngo.org
        self.assertEqual(org.getLocalProperty('keywords', 'en'),
                         'European Ecotourism Network')

    def test_contact_edit_recomputes_geo_type(self):
        addNyContact(self.portal['market-place'], id='c1', title='C1',
                     contributor='manager',
                     **{'category-organization': 'ngo'})
        ob = self.portal['market-place'].c1
        self.assertEqual(ob.geo_type, 'ngo')
        ob.saveProperties(title='C1', **{
            'category-organization': 'ngo',
            'category-supporting-solutions': 'green'})
        self.assertEqual(ob.geo_type, 'green')

    def test_publisher_permission(self):
        self.browser._twill._client.headers.pop('Authorization')
        self.browser.go(PUBLISHER_URL + '/disseminate_url')
        self.assertIn('/login_html', self.browser.get_url())

    def test_no_country_pointers(self):
        # pointer auto-creation was removed in #4463
        addNyURL(self.portal.resources, id='url', title='url',
                 coverage='Georgia, South Georgia', topics=['atopic'],
                 locator='http://eaudeweb.ro', contributor='manager')
        catalog = self.portal.getCatalogTool()
        self.assertEqual(len(catalog(meta_type='Naaya URL')), 1)
        self.assertEqual(len(catalog(meta_type='Naaya Pointer')), 0)
        for country in self.portal.countries.objectValues():
            self.assertEqual(country.objectIds(), [])
