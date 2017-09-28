import re
import time
from os import path
import random

from nose.plugins.skip import SkipTest
import transaction
from AccessControl.Permission import Permission
from zope.component import getGlobalSiteManager

from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase
from naaya.core.tests import mock_captcha
from Products.Naaya.adapters import FolderMetaTypes

fixtures_path = path.join(path.dirname(__file__), 'fixtures')

def _wait_for(callback, fail_message=None, timeout=5.):
    from time import time, sleep
    t0 = time()
    while time() < t0 + timeout:
        if callback():
            return
        sleep(0.1)
    if fail_message is None:
        fail_message = ( "Condition was not true after %.2f seconds: %r" %
                         (float(timeout), repr(callback)) )
    assert False, fail_message

def login_with(username, password):
    """ make a decorator that runs the test while logged in """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.login_user(username, password)
            transaction.abort()
            func(self, *args, **kwargs)
            self.logout_user()
        wrapper.func_name = func.func_name
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator

def with_mock_captcha(func):
    def wrapper(self, *args, **kwargs):
        gsm = getGlobalSiteManager()
        mock_captcha_provider = mock_captcha.create_mock()
        gsm.registerAdapter(mock_captcha_provider)
        try:
            return func(self, *args, **kwargs)
        finally:
            gsm.unregisterAdapter(mock_captcha_provider)
    wrapper.func_name = func.func_name
    wrapper.__doc__ = func.__doc__
    return wrapper

class _CommonContentTests(SeleniumTestCase):
    """
    Common testing logic for Naaya content types. Because the name starts
    with '_', nose will ignore this class.
    """

    def setUp(self):
        self.rnd = ''.join(random.choice("0123456789") for c in range(6))

    def tearDown(self):
        # maybe the test failed while inside a window or frame
        self.selenium.select_window('')
        self.selenium.select_frame('relative=top')

    _index_contributor_full_name = False
    def _assert_index_ok(self, ob):
        """
        Called by `test_index` below to verify that the index page is rendered
        correctly. May be overridden by subclasses but it's probably a good
        idea to call super.
        """
        txt = self.selenium.get_text

        assert ("Test Object %s" % self.rnd) in txt('//h1')

        releasedate_txt = ob.releasedate.strftime('%d/%m/%Y')
        assert txt('//tr[th[text()="Release date"]]/td') == releasedate_txt

        if self._index_contributor_full_name:
            contrib_name = "Contributor Test"
        else:
            contrib_name = 'contributor'
        assert txt('//tr[th[text()="Contributor"]]/td') == contrib_name

        desc_ok = ("A few words about our test object. "
                   "The random value is %s." % self.rnd)
        assert txt('css=p.content-test') == desc_ok

    def test_index(self):
        """
        Check the index page as seen by both anonymous and logged-in users.
        """
        container = self.portal['info']
        title = "Test Object %s" % self.rnd
        ob_id = self._add_object_extra(container, title=title)
        transaction.commit()

        self.selenium.open('/portal/info/%s' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        transaction.abort()
        ob = container[ob_id]
        self._assert_index_ok(ob)

        self.login_user('contributor', 'contributor')
        self.selenium.open('/portal/info/%s' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        transaction.abort()
        ob = container[ob_id]
        self._assert_index_ok(ob)
        self.logout_user()

    def test_index_no_showcontributor(self):
        """ Make sure the `display_contributor` option works. """
        # TODO this test is skipped because the `display_contributor` setting
        # is not being honoured currently
        raise SkipTest

        container = self.portal['info']
        title = "Test Object %s" % self.rnd
        ob_id = self._add_object_plain(container, title=title)
        self.portal.display_contributor = '' # meaning "false"
        transaction.commit()

        self.selenium.open('/portal/info/%s' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        is_element = self.selenium.is_element_present
        assert not is_element('//th[text()="Contributor"]')

    @login_with('contributor', 'contributor')
    def test_add(self):
        """ Add a content object and check that it was saved properly. """
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium.select('typetoadd', 'label=%s' % self.meta_label)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self._fill_add_form()
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        # requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        transaction.abort()
        self._assert_object_added_properly(self.portal['info'])

    def _fill_add_form(self):
        """
        Fill out the "add object" form in the browser. Subclasses should
        override this to insert additional required fields.
        """
        self.selenium.type('title', u"Test Object %s" % self.rnd)
        self.selenium.type('coverage', u"Country")
        self.selenium.type('keywords', u"short, story, test story")
        self.selenium.type('sortorder', u"125")
        self.selenium.click('discussion')

    def _assert_object_added_properly(self, container,
                                      submitter='contributor'):
        """
        Called by `test_add` above to verify that the object was saved
        correctly. May be overridden by subclasses but it's probably a good
        idea to call super.
        """
        ob_id = "test-object-%s" % self.rnd
        assert ob_id in container.objectIds()
        ob = container[ob_id]
        assert ob.submitted == True
        assert ob.approved == False
        assert ob.contributor == submitter

    def add_object(self, parent, **kwargs):
        raise NotImplementedError # should be implemented by subclasses

    def _add_object_plain(self, parent, **kwargs):
        """
        Add a minimal object of the current content type. Another method,
        `_add_object_extra`, may be used to add an object with more properties
        (e.g. a BFile object with an uploaded file or a fully filled-out Event
        object).
        """
        self.login('contributor')
        ob_id = self.add_object(parent, **kwargs)
        self.logout()
        return ob_id

    def _add_object_extra(self, parent, **kwargs):
        """
        Add an elaborate object with many properties, so we can test more of
        the current content type's features. By default it simply calls
        `_add_object_plain` with an additional "description" value, but
        subclasses are encouraged to override.
        """
        kwargs['description'] = (
            '<p class="content-test">'
            'A few words about our test object. The random value is %s.'
            '</p>') % self.rnd
        return self._add_object_plain(parent, **kwargs)

    @login_with('contributor', 'contributor')
    def test_edit_title(self):
        """ Edit the object's title (a simple editing operation). """
        container = self.portal['info']
        title = "Test Object %s" % self.rnd
        ob_id = self._add_object_plain(container, title=title)
        transaction.commit()

        self.selenium.open('/portal/info/%s/edit_html' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        assert self.selenium.get_value('title') == u"Test Object %s" % self.rnd
        new_title = u"Changed title for %s" % self.rnd
        self.selenium.type("title", new_title)
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        assert self.selenium.is_text_present("Saved changes.")
        assert self.selenium.get_value("title") == new_title
        transaction.abort()
        assert container[ob_id].title == new_title

    def _get_image_container(self, ob):
        """
        Get the container where TinyMCE images for `obj` are saved. It's
        usually the 'images' folder in the site, but for some objects this
        may be different.
        """
        return ob.getSite()['images']

    @login_with('contributor', 'contributor')
    def test_edit_description(self):
        """ An elaborate test that uploads an image in the TinyMCE editor. """
        container = self.portal['info']
        title = "Test Object %s" % self.rnd
        ob_id = self._add_object_plain(container, title=title)
        transaction.commit()
        ob = container[ob_id]
        assert self._get_image_container(ob).objectIds() == []

        self.selenium.open('/portal/info/%s/edit_html' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        # 'span.mceIcon.mce_image' is the TinyMCE button for inserting an image
        self.selenium.wait_for_condition("""
            window.jQuery('span.mceIcon.mce_image').length > 0
            """, self._selenium_page_timeout)

        self.selenium.click("//span[@class='mceIcon mce_image']")
        # wait for the iframe to load
        self.selenium.wait_for_condition("""
            (window.jQuery('div.mceMiddle iframe')[0]
             .contentDocument.readyState) == 'complete'
            """, self._selenium_page_timeout)

        img_selector = "//body[@id='tinymce']//p/img"
        #img_selector = "//body[@id='tinymce']//img[@id='fe_img_preview']"
        self.selenium.select_frame('//iframe[@id="description_ifr"]')
        assert not self.selenium.is_element_present(img_selector)
        self.selenium.select_frame('relative=top') # back to main frame

        self.selenium.select_frame('//div[@class="mceMiddle"]//iframe')
        self.selenium.click('//li[@id="computer_tab"]//a')

        img_path = path.join(fixtures_path, 'img.gif')
        self.selenium.type('file', img_path)

        #_wait_for(lambda: self.selenium.is_element_present(
        #                '//body/div/div/img[@id="fe_img_preview"]'))
        #_wait_for(lambda: self.selenium.is_element_present(
        #                '//input[@value="Insert"]'))
        import time; time.sleep(1) # TODO: use some "wait_for" instead of sleep

        self.selenium.click('//input[@value="Insert"]')
        self.selenium.select_frame('relative=top') # back to main frame

        self.selenium.select_frame('//iframe[@id="description_ifr"]')
        _wait_for(lambda: self.selenium.is_element_present(img_selector))
        self.selenium.select_frame('relative=top')
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        transaction.abort()
        p = r'<img[^>]* src="/portal/images/img.gif"'
        assert re.search(p, ob.description) is not None
        assert self._get_image_container(ob).objectIds() == ['img.gif']

        self.selenium.click('link=Back to index')
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_element_present(
            '//div[@id="middle_port"]//p/img')
        assert self.selenium.is_element_present(
            '//div[@id="middle_port"]//p/img[@src="/portal/images/img.gif"]')

        img_complete = self.selenium.get_eval(
                    "window.jQuery('div#middle_port p img')[0].complete")
        img_src = self.selenium.get_eval(
                    "window.jQuery('div#middle_port p img')[0].src")

        assert img_complete == "true", "Image does not show up in the browser"
        assert img_src.endswith("img.gif"), ("Not the right image, perhaps "
                                             "there are more")

    def _fill_edit_form_with_error(self):
        """
        Introduce an error in the edit form so that changes are not saved and
        we get an error message.
        """
        self.selenium.type("title", "")

    @login_with('contributor', 'contributor')
    def test_edit_with_error(self):
        """
        Edit object, but introduce an error, to check that we get the error
        message.
        """
        container = self.portal['info']
        title = "Test Object %s" % self.rnd
        ob_id = self._add_object_plain(container, title=title)
        transaction.commit()

        self.selenium.open('/portal/info/%s/edit_html' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self._fill_edit_form_with_error()
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self._assert_edit_page_error()

    def _assert_edit_page_error(self):
        """
        Verify that the error message shows up. Subclasses may need to override
        this.
        """
        assert self.selenium.is_text_present(
            "The form contains errors. Please correct them and try again.")
        assert self.selenium.is_text_present('Value required for "Title"')

    def _add_glossary(self, glossary_id, xliff_name):
        from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
        manage_addGlossaryCentre(self.portal, glossary_id,
                                 "Glossary %s" % glossary_id)
        glossary = self.portal[glossary_id]
        xliff_file = open(path.join(fixtures_path, xliff_name), 'rb')
        glossary.xliff_import(xliff_file.read())
        xliff_file.close()

    @login_with('contributor', 'contributor')
    def test_aaaaaakeywords(self):
        """ Check autocomplete functionality and the button "pick"
        (from glossary) for keywords

        XXX: Test multiple_select render as well

        """
        self._add_glossary('test_glossary_kwds', 'glossary.xliff')
        schema_tool = self.portal['portal_schemas']
        schema = schema_tool.getSchemaForMetatype(self.meta_type)
        schema.getWidget('keywords').glossary_id = 'test_glossary_kwds'
        transaction.commit()

        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium.select('typetoadd', 'label=%s' % self.meta_label)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self._fill_add_form()
        self.selenium.type('keywords', u"") #Clear field
        self.selenium.type_keys('keywords', u"Hol")
        self.selenium.wait_for_condition('window.selenium_ready == true',
                                         self._selenium_page_timeout)
        #Should be displayed and an autocomplete option
        self.selenium.is_text_present(u'Holy hand grenade')

        self.selenium.click("//input[@type='button'][@value='Pick']")
        self.selenium.wait_for_condition('window.selenium_ready == true',
                                         self._selenium_page_timeout)
        self.selenium.click("//li[@type='element'][2]/a")
        time.sleep(1)
        assert self.selenium.get_value("keywords") == u'Ni,'
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        transaction.abort()
        ob = self.portal['info']['test-object-%s' % self.rnd]
        self.assertEqual(ob.keywords, u'Ni,')

    @with_mock_captcha
    def test_with_captcha(self):
        """
        Test for captcha: does it show up when it's supposed to? Is it really
        verified?
        """
        self.portal.acl_users._doAddUser('other_user', 'other_user', [], '',
                                    'Other', 'User', 'other_user@example.com')
        zperm = self.portal.get_pluggable_item(self.meta_type)['permission']
        p = Permission(zperm, (), self.portal)
        p.setRoles(p.getRoles() + ['Authenticated'])
        transaction.commit()

        self.login_user('other_user', 'other_user')

        self.selenium.open('/portal/info/', True)
        self.selenium.select('typetoadd', 'label=%s' % self.meta_label)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        assert self.selenium.is_element_present(
                '//input[@name="test-captcha-response"]')

        self._fill_add_form()

        # submit with no captcha response
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Verification words do not match "
                                             "the ones in the picture.")

        # submit with incorrect captcha response
        self.selenium.type('test-captcha-response', "blah blah")
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present("Verification words do not match "
                                             "the ones in the picture.")

        challenge = self.selenium.get_text(
                '//span[@id="test-captcha-challenge"]')
        response = mock_captcha.solve(challenge)
        self.selenium.type('test-captcha-response', response)

        # submit with proper response
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.is_text_present('The administrator will analyze')

        transaction.abort()
        self._assert_object_added_properly(self.portal['info'],
                                           submitter='other_user')

        # "skip captcha" permission
        p = Permission('Naaya - Skip Captcha', (), self.portal)
        p.setRoles(p.getRoles() + ['Authenticated'])
        transaction.commit()

        self.selenium.open('/portal/info/', True)
        self.selenium.select('typetoadd', 'label=%s' % self.meta_label)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        assert not self.selenium.is_element_present(
                '//input[@name="test-captcha-response"]')

        self.logout_user()

    @login_with('admin', '')
    def test_switch_language(self):
        """ Move content from one language to another. """
        self.portal.gl_add_site_language('fr')
        self.portal.switch_language = 'on'
        container = self.portal['info']
        title = "Test Object %s" % self.rnd
        ob_id = self._add_object_plain(container, title=title)
        ob = container[ob_id]
        transaction.commit()

        assert ob.getLocalProperty('title', 'en') == title
        assert ob.getLocalProperty('title', 'fr') == ''

        self.selenium.open('/portal/info/%s/edit_html' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium.click('//form[@name="switch_to_language"]'
                            '/input[@type="submit"]')
        self.selenium.get_confirmation()
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        assert self.selenium.get_location().endswith('/edit_html?lang=fr')

        transaction.abort()
        assert ob.getLocalProperty('title', 'en') == ''
        assert ob.getLocalProperty('title', 'fr') == title

class FolderTest(_CommonContentTests):
    meta_label = "Folder"
    meta_type = "Naaya Folder"

    def _assert_index_ok(self, ob):
        assert ("Test Object %s" % self.rnd) in self.selenium.get_text('//h1')

    def test_index_anonymous(self):
        raise SkipTest

    def add_object(self, parent, **kwargs):
        from Products.Naaya.NyFolder import addNyFolder
        return addNyFolder(parent, **kwargs)

    def test_with_captcha(self):
        # TODO folders don't ever ask for captcha. maybe they should.
        raise SkipTest

    def _fill_edit_form_with_error(self):
        # Folders are allowed to have a blank title so, when running
        # test_edit_with_error, submit a blank value for "sort order".
        self.selenium.type("sortorder", "")

    def _assert_edit_page_error(self):
        assert self.selenium.is_text_present(
            "The form contains errors. Please correct them and try again.")
        assert self.selenium.is_text_present('Value required for "Sort order"')

class NewsTest(_CommonContentTests):
    meta_label = "News"
    meta_type = "Naaya News"

    def add_object(self, parent, **kwargs):
        from naaya.content.news.news_item import addNyNews
        return addNyNews(parent, **kwargs)

class StoryTest(_CommonContentTests):
    meta_label = "Story"
    meta_type = "Naaya Story"

# TODO stories should be containers for their own images
#    def _get_image_container(self, ob):
#        return ob
#
    def add_object(self, parent, **kwargs):
        from naaya.content.story.story_item import addNyStory
        return addNyStory(parent, **kwargs)

class DocumentTest(_CommonContentTests):
    meta_label = "HTML Document"
    meta_type = "Naaya Document"

# TODO stories should be containers for their own images
#    def _get_image_container(self, ob):
#        return ob
#
    def add_object(self, parent, **kwargs):
        from naaya.content.document.document_item import addNyDocument
        return addNyDocument(parent, **kwargs)

class PointerTest(_CommonContentTests):
    meta_label = "Pointer"
    meta_type = "Naaya Pointer"

    def add_object(self, parent, **kwargs):
        from naaya.content.pointer.pointer_item import addNyPointer
        return addNyPointer(parent, **kwargs)

class UrlTest(_CommonContentTests):
    meta_label = "URL"
    meta_type = "Naaya URL"

    def add_object(self, parent, **kwargs):
        from naaya.content.url.url_item import addNyURL
        return addNyURL(parent, **kwargs)

class EventTest(_CommonContentTests):
    meta_label = "Event"
    meta_type = "Naaya Event"
    _index_contributor_full_name = True

    def _add_object_extra(self, parent, **kwargs):
        for name in ('location', 'location_address', 'host', 'contact_person',
                     'contact_email', 'contact_phone', 'contact_fax'):
            kwargs[name] = "Test value for '%s' (rnd %s)'" % (name, self.rnd)
        url_base = "http://example.com/%s" % self.rnd
        kwargs['location_url'] = url_base + "/location"
        kwargs['agenda_url'] = url_base + "/agenda"
        kwargs['event_url'] = url_base + "/event"
        kwargs['start_date'] = '02/11/2010'
        kwargs['end_date'] = '04/11/2010'
        return super(EventTest, self)._add_object_extra(parent, **kwargs)

    def _assert_index_ok(self, ob):
        super(EventTest, self)._assert_index_ok(ob)
        txt = self.selenium.get_text
        period_ok = "[02/11/2010 - 04/11/2010]"
        assert txt('//tr[th[text()="Period"]]/td') == period_ok
        # TODO chek that all values injected by _add_object_extra show up on
        # the page

    def _fill_add_form(self):
        super(EventTest, self)._fill_add_form()
        self.selenium.type('start_date', "05/11/2010")

    def add_object(self, parent, **kwargs):
        from naaya.content.event.event_item import addNyEvent
        if 'start_date' not in kwargs:
            kwargs['start_date'] = "05/11/2010"
        return addNyEvent(parent, **kwargs)

class FileTest(_CommonContentTests):
    meta_label = "File"
    meta_type = "Naaya File"

    def add_object(self, parent, **kwargs):
        from naaya.content.file.file_item import addNyFile
        return addNyFile(parent, **kwargs)

class BlobFileTest(_CommonContentTests):
    meta_label = "File"
    meta_type = "Naaya Blob File"
    _index_contributor_full_name = True

    def add_object(self, parent, **kwargs):
        from naaya.content.bfile.bfile_item import addNyBFile
        return addNyBFile(parent, **kwargs)

    def setUp(self):
        super(BlobFileTest, self).setUp()
        # "Naaya Blob File" is not installed by default
        self.portal.manage_uninstall_pluggableitem("Naaya File")
        self.portal.manage_install_pluggableitem("Naaya Blob File")
        FolderMetaTypes(self.portal.info).add("Naaya Blob File")
        transaction.commit()

    def _assert_object_added_properly(self, container, *args, **kwargs):
        super(BlobFileTest, self)._assert_object_added_properly(
                container, *args, **kwargs)
        # make sure the right content type was added
        ob = container["test-object-%s" % self.rnd]
        assert ob.meta_type == "Naaya Blob File"

    @login_with('contributor', 'contributor')
    def test_upload(self):
        """ Test the BFile upload functionality. """
        self.selenium.open('/portal/info/', True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self.selenium.select('typetoadd', 'label=%s' % self.meta_label)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        img_path = path.join(fixtures_path, 'img.gif')
        self.selenium.type('uploaded_file', img_path)
        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        # requires approval
        assert self.selenium.is_text_present('The administrator will analyze')

        transaction.abort()
        container = self.portal['info']
        ob_id = "img" # BFile constructs IDs based on the filename
        assert ob_id in container.objectIds()
        ob = container[ob_id]
        assert ob.title == "img"
        assert ob.submitted == True
        assert ob.approved == False
        assert ob.contributor == 'contributor'

        f = open(img_path, 'rb')
        img_data = f.read()
        f.close()
        assert ob.current_version.filename == "img.gif"
        assert ob.current_version.size == len(img_data)
        assert ob.current_version.content_type == "image/gif"
        f = ob.current_version.open()
        assert f.read() == img_data
        f.close()
