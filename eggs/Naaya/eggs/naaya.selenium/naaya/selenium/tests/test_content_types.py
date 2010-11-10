import re
import time
import os
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase


class NaayaContentTypesTestCase(SeleniumTestCase):
    """ All tests in this TestCase follow a CRUD pattern"""
    def afterSetUp(self):
        self.login_user('contributor', 'contributor')

    def test_folder(self):
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=Folder')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type('title', u'Test Naaya Folder')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.click('discussion')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')
        assert self.selenium.is_text_present('Test Naaya Folder')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-folder", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium.click('//input[@name="id" and @value="test-naaya-folder"]')
        self.selenium.click("deleteObjects:method")
        time.sleep(1)
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_news(self):
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=News')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya News')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.click('discussion')
        self.selenium.type('expirationdate','01/01/2010')
        self.selenium.type('resourceurl', u'http://www.example.com/')
        self.selenium.type('source', u'http://www.example.com/')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')
        assert self.selenium.is_text_present('Test Naaya News')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-news", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click('//input[@name="id" and @value="test-naaya-news"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_story(self):
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=Story')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya Story')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.click('discussion')
        self.selenium.type('resourceurl', u'http://www.example.com/')
        self.selenium.type('source', u'http://www.example.com/')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')
        assert self.selenium.is_text_present('Test Naaya Story')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-story", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click('//input[@name="id" and @value="test-naaya-story"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_html_document(self):
        """ Some kind of checking for tinymce is needed """
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=HTML Document')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya HTML Document')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.click('discussion')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-html-document", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click(
            '//input[@name="id" and @value="test-naaya-html-document"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_pointer(self):
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=Pointer')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya Pointer')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.type('redirect', u'/portal/info')
        self.selenium.click('discussion')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-pointer", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click(
            '//input[@name="id" and @value="test-naaya-pointer"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_url(self):
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=URL')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya URL')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.click('discussion')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-url", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click(
            '//input[@name="id" and @value="test-naaya-url"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_event(self):
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=Event')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya Event')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.type('start_date', '18/10/2010')
        self.selenium.type('start_date', '18/10/2010')
        self.selenium.click('link=Event')
        self.selenium.click('discussion')
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/test-naaya-event", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click(
            '//input[@name="id" and @value="test-naaya-event"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")

    def test_file(self):
        #Add
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.select('typetoadd', 'label=File')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('Value required for "Title"')

        self.selenium.type('title', u'Test Naaya File')
        self.selenium.type('coverage', u'Country')
        self.selenium.type('keywords', u'short, story, test story')
        self.selenium.type('sortorder', u'125')
        self.selenium.type('file', (os.path.dirname(__file__) +
                           '/fixtures/img.gif'))
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        #Requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        #Edit
        self.selenium.click("//td[@class='edit']/a")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.type("title", u"Changed title")
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == u'Changed title'

        #View
        self.selenium.open("/portal/info/img.gif", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Changed title")
        assert self.selenium.is_text_present("Download")

        #Login as admin and delete
        self.logout_user()
        self.login_user('admin', '')
        self.selenium.open("/portal/info/", True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self.selenium.click(
            '//input[@name="id" and @value="img.gif"]')
        self.selenium.click("deleteObjects:method")
        self.failUnless(re.search(r"^Are you sure[\s\S]$",
                                  self.selenium.get_confirmation()))
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Item(s) deleted.")
        assert not self.selenium.is_text_present("Changed title")
