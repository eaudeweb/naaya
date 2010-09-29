from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase


class NaayaDocumentTest(SeleniumTestCase):
    def selenium_initialize(self):
        """
        Steps:
        1.Login as Contributor
        2.Open Information
        3.Add an item
        !Atention the items added in this test do not complete the language,
        meaning it remains default, the description as well, or if it's the case
        the test does not use importing pictures
        """
        self.login_user('contributor','contributor')
        selen = self.selenium
        selen.open('/portal')
        selen.wait_for_page_to_load('15000')
        selen.click('link=Information')
        selen.wait_for_page_to_load('15000')
        self.assertTrue(selen.is_element_present('typetoadd'),
                        'An error occured while trying to access `typetoadd` select field name!')

    def test_basic_story(self):
        self.selenium_initialize()
        selen = self.selenium

        add_story_data = {
            'laguage': 'English',
            'title': 'Test Naaya Story',
            'geo coverage': 'Country',
            'keywords': 'short, story, test story',
            'sortorder': '125',
            'release date': '',  #must be dd/mm/yyyy or none for today
            'comments': True,
            'resource_url': 'http://www.example.com/',
            'source': 'http://www.example.com/',
            'picture_url': '',  #just type a picture url from your pc
        }
        self.selenium_add_story(add_story_data)
        self.assertFalse(selen.is_text_present('Error'),
                         'Adding a new story failed')
        self.assertTrue(selen.is_text_present(add_story_data['title']))

    def selenium_add_story(self, add_story_data):
        selen = self.selenium
        selen.select('typetoadd', 'label=Story')
        selen.wait_for_page_to_load('30000')

        selen.type('title', add_story_data['title'])
        selen.type('coverage',add_story_data['geo coverage'])
        selen.type('keywords', add_story_data['keywords'])
        selen.type('sortorder', add_story_data['sortorder'])
        if add_story_data['release date']:
            selen.click('link=Today')
        else:
            selen.type('releasedate', add_story_data['release date'])
        if not add_story_data['comments']: selen.click('discussion')
        selen.type('resourceurl', add_story_data['resource_url'])
        selen.type('source', add_story_data['source'])
        if add_story_data['picture_url']:
            selen.type('frontpicture', add_story_data['picture_url'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load('30000')

    def test_basic_news(self):
        self.selenium_initialize()
        selen = self.selenium
        news_data = {
            'title': 'Test news',
            'description': 'news description',
            'geo_coverage': 'Region',
            'keywords': 'test,something',
            'comments': True,
            'sort_order': '123',
            'release_date': '',  #like dd/mm/yyyy
            'details': 'some specifications',
            'expiration_date': '15/07/2021',  #like dd/mm/yyyy
            'concerned_url': 'www.example.ro',
            'source': 'source',
        }

        self.selenium_add_news(news_data)
        self.assertFalse(selen.is_text_present('Error'),
                         'Adding news failed')
        self.assertTrue(selen.is_text_present(news_data['title']))

    def selenium_add_news(self, news_data):
        """add news without picture"""
        selen = self.selenium
        selen.open('/portal/info', True)
        selen.select('typetoadd', 'label=News')
        selen.wait_for_page_to_load('30000')

        selen.type('title', news_data['title'])
        selen.type('coverage', news_data['geo_coverage'])
        selen.type('keywords', news_data['keywords'])
        if not news_data['release_date']:
            selen.click('link=Today')
        else:
            selen.type('releasedate', news_data['releade_date'])
        if news_data['comments']:
            selen.click('discussion')
        if news_data['expiration_date']:
            selen.type('expirationdate', news_data['expiration_date'])
        selen.type('resourceurl', news_data['concerned_url'])
        selen.type('source', news_data['source'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load('30000')

    def test_basic_folder(self):
        self.selenium_initialize()
        selen = self.selenium
        new_folder_data = {
            'title': 'test folder',
            'coverage': 'earth',
            'keywords': 'key',
            'release_date': '',  #like dd/mm/yyyy
            'comments': True,
            'sortorder': '123',
            'maintainer_email': 'email@example.com',
        }
        self.selenium_add_new_folder(new_folder_data)
        self.assertFalse(selen.is_text_present('Error'),
                         'Adding a new folder failed')

        self.assertTrue(selen.is_text_present(new_folder_data['title']))

    def selenium_add_new_folder(self, new_folder_data):
        selen = self.selenium
        selen.open('/portal/info', True)
        selen.select('typetoadd', 'label=Folder')
        selen.wait_for_page_to_load('30000')

        selen.type('title', new_folder_data['title'])
        selen.type('coverage', new_folder_data['coverage'])
        selen.type('keywords', new_folder_data['keywords'])
        if new_folder_data['sortorder']:
            selen.type('sortorder', new_folder_data['sortorder'])
        if new_folder_data['release_date']:
            selen.type('releasedate', new_folder_data['release_date'])
        else:
            selen.click('link=Today')
        if new_folder_data['comments']:
            selen.check('discussion')
        else:
            selen.uncheck('discussion')
        selen.type('maintainer_email', new_folder_data['maintainer_email'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load('30000')

    def test_basic_url(self):
        selen = self.selenium
        self.selenium_initialize()
        url_data = {
            'title': 'Test URL',
            'coverage': 'earth',
            'keywords': 'key',
            'release_date': '',  #like dd/mm/yyyy
            'comments': True,
            'sortorder': '123',
        }
        self.selenium_add_url(url_data)

        self.assertFalse(selen.is_text_present('Error'),
                         'Adding url failed')
        self.assertTrue(selen.is_text_present(url_data['title']))

    def selenium_add_url(self, url_data):
        selen = self.selenium
        selen.open('/portal/info/index_html', True)
        selen.select('typetoadd', 'label=URL')
        selen.wait_for_page_to_load('30000')

        selen.type('title', url_data['title'])
        selen.type('coverage', url_data['coverage'])
        selen.type('keywords', url_data['keywords'])
        if url_data['sortorder']:
            selen.type('sortorder', url_data['sortorder'])
        if url_data['release_date']:
            selen.type('releasedate', url_data['release_date'])
        else:
            selen.click('link=Today')
        if url_data['comments']:
            selen.check('discussion')
        else:
            selen.uncheck('discussion')
        selen.click('redirect')
        selen.type('locator', 'http://example.com')
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load('30000')

    def test_basic_HTML_Document(self):
        selen = self.selenium
        self.selenium_initialize()
        html_fixture = {
            'title': 'Test html document',
            'coverage': 'geographical area',
            'keywords': 'key, words',
            'sortorder': '123',
            'release_date': '',  #like dd/mm/yyyy
            'comments': True,
        }
        self.selenium_add_html(html_fixture)

        self.assertFalse(selen.is_text_present('Error'),
                         'Adding a html document failed')
        self.assertTrue(selen.is_text_present(html_fixture['title']))

    def selenium_add_html(self, html_fixture):
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.select("typetoadd", "label=HTML Document")
        selen.wait_for_page_to_load("30000")

        selen.type("title", html_fixture['title'])
        selen.type("coverage", html_fixture['coverage'])
        selen.type("keywords", html_fixture['keywords'])
        if html_fixture['sortorder']:
            selen.type('sortorder', html_fixture['sortorder'])
        if html_fixture['release_date']:
            selen.type('releasedate', html_fixture['release_date'])
        else:
            selen.click('link=Today')
        if html_fixture['comments']:
            selen.check('discussion')
        else:
            selen.uncheck('discussion')
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load("30000")

    def test_basic_pointer(self):
        self.selenium_initialize()
        selen = self.selenium
        pointer_data = {
            'title': 'Test pointer',
            'coverage': 'geographical area',
            'keywords': 'key, words',
            'sortorder': '123',
            'release_date': '',  #like dd/mm/yyyy
            'comments': True,
            'redirect': True,
            'pointer': 'info',
        }
        self.selenium_add_pointer(pointer_data)

        self.assertFalse(selen.is_text_present('Error'),
                         'Adding a pointer failed')
        self.assertTrue(selen.is_text_present(pointer_data['title']))

    def selenium_add_pointer(self, pointer_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.select("typetoadd", "label=Pointer")
        selen.wait_for_page_to_load("30000")

        selen.type("title", pointer_data['title'])
        selen.type("coverage", pointer_data['coverage'])
        selen.type("keywords", pointer_data['keywords'])
        if pointer_data['sortorder']:
            selen.type('sortorder', pointer_data['sortorder'])
        if pointer_data['release_date']:
            selen.type('releasedate', pointer_data['release_date'])
        else:
            selen.click('link=Today')
        if pointer_data['comments']:
            selen.check('discussion')
        else:
            selen.uncheck('discussion')
        if pointer_data['redirect']:
            selen.check('redirect')
        else:
            selen.uncheck('redirect')
        selen.type('pointer', pointer_data['pointer'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load("30000")

    def test_basic_event(self):
        self.selenium_initialize()
        selen = self.selenium
        event_data = {
            'title': 'Test event',
            'coverage': 'geographical area',
            'keywords': 'key, words',
            'sortorder': '123',
            'release_date': '',  #like dd/mm/yyyy
            'comments': True,
            'location': 'location example',
            'location_address': 'adress',
            'location_url': 'www.example.com/location',
            'event_type': 'Meeting',
            'host': 'event host',
            'event_url': 'www.example.com/event',
            'agenda_url': 'www.example.com/agenda',
            'contact_person': 'Popescu vasile',
            'contact_email': 'email@example.com',
            'contact_phone': '021 01 01 001',
            'contact_fax': '021 01 00 001',
            'start_date': '20/10/2010',  #like dd/mm/yyyy
            'end_date': '12/12/2011',  #like dd/mm/yyyy
        }
        self.selenium_add_event(event_data)

        self.assertFalse(selen.is_text_present('Error'),
                         'Adding an event failed')
        self.assertTrue(selen.is_text_present(event_data['title']))

    def selenium_add_event(self, event_data):
        """there are more then one link named today
        so if the start date is not filled in the test may fail"""
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.select("typetoadd", "label=Event")
        selen.wait_for_page_to_load("30000")

        selen.type("title", event_data['title'])
        selen.type("coverage", event_data['coverage'])
        selen.type("keywords", event_data['keywords'])
        if event_data['sortorder']:
            selen.type('sortorder', event_data['sortorder'])
        if event_data['release_date']:
            selen.type('releasedate', event_data['release_date'])
        else:
            selen.click('link=Today')
        if event_data['comments']:
            selen.check('discussion')
        else:
            selen.uncheck('discussion')
        selen.type("location", event_data['location'])
        selen.type("location_address", event_data['location_address'])
        selen.type("location_url", event_data['location_url'])
        if event_data['start_date']:
            selen.type('start_date', event_data['start_date'])
        else:
            selen.click('link=Today')
        if event_data['end_date']:
            selen.type('end_date', event_data['end_date'])
        selen.type("host", event_data['host'])
        selen.type("agenda_url", event_data['agenda_url'])
        selen.type("event_url", event_data['event_url'])
        if event_data['event_type']:
            selen.click("topitem")
            selen.click("link=%s" % event_data['event_type'])
        selen.type("contact_person", event_data['contact_person'])
        selen.type("contact_email", event_data['contact_email'])
        selen.type("contact_phone", event_data['contact_phone'])
        selen.type("contact_fax", event_data['contact_fax'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load("30000")

    def test_basic_file(self):
        """using a file example from url, from own computer not tested"""
        self.selenium_initialize()
        selen = self.selenium
        file_data = {
            'title': 'Test file',
            'coverage': 'geographical area',
            'keywords': 'key, words',
            'sortorder': '123',
            'release_date': '',  #like dd/mm/yyyy
            'comments': True,
            'url': 'example.com/file.txt',
        }
        self.selenium_add_file(file_data)

        self.assertFalse(selen.is_text_present('Error'),
                         'Adding a file failed')
        self.assertTrue(selen.is_text_present(file_data['title']))

    def selenium_add_file(self, file_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.select("typetoadd", "label=File")
        selen.wait_for_page_to_load("30000")

        selen.type("title", file_data['title'])
        selen.type("coverage", file_data['coverage'])
        selen.type("keywords", file_data['keywords'])
        if file_data['sortorder']:
            selen.type('sortorder', file_data['sortorder'])
        if file_data['release_date']:
            selen.type('releasedate', file_data['release_date'])
        else:
            selen.click('link=Today')
        if file_data['comments']:
            selen.check('discussion')
        else:
            selen.uncheck('discussion')
        selen.click("source-url")
        selen.type("url", file_data['url'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load("30000")