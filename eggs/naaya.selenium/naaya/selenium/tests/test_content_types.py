import re
import time
from os import path
import random

import transaction
from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

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

class _CommonContentTests(SeleniumTestCase):
    """
    Common testing logic for Naaya content types. Because the name starts
    with '_', nose will ignore this class.
    """

    def setUp(self):
        self.rnd = ''.join(random.choice("0123456789") for c in range(6))
        self.login_user('contributor', 'contributor')

    def tearDown(self):
        # maybe the test failed while inside a window or frame
        self.selenium.select_window('')
        self.selenium.select_frame('relative=top')
        self.logout_user()

    def test_add(self):
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
        self.selenium.type('title', u"Test Object %s" % self.rnd)
        self.selenium.type('coverage', u"Country")
        self.selenium.type('keywords', u"short, story, test story")
        self.selenium.type('sortorder', u"125")
        self.selenium.click('discussion')

    def _assert_object_added_properly(self, container):
        ob_id = "test-object-%s" % self.rnd
        assert ob_id in container.objectIds()
        ob = container[ob_id]
        assert ob.submitted == True
        assert ob.approved == False
        assert ob.contributor == 'contributor'

    def _add_object(self, parent, **kwargs):
        transaction.abort()
        self.login('contributor')
        ob_id = self.add_object(parent, **kwargs)
        self.logout()
        transaction.commit()
        return ob_id

    def test_edit_title(self):
        container = self.portal['info']
        ob_id = self._add_object(container, title="Test Object %s" % self.rnd)

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
        return ob.getSite()['images']

    def test_edit_description(self):
        container = self.portal['info']
        ob_id = self._add_object(container, title="Test Object %s" % self.rnd)
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
        self.selenium.type("title", "")

    def test_edit_with_error(self):
        container = self.portal['info']
        ob_id = self._add_object(container, title="Test Object %s" % self.rnd)

        self.selenium.open('/portal/info/%s/edit_html' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self._fill_edit_form_with_error()
        self.selenium.click("//input[@value='Save changes']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        self._assert_edit_page_error()

    def _assert_edit_page_error(self):
        assert self.selenium.is_text_present(
            "The form contains errors. Please correct them and try again.")
        assert self.selenium.is_text_present('Value required for "Title"')

    def test_view(self):
        container = self.portal['info']
        ob_id = self._add_object(container, title="Test Object %s" % self.rnd)
        self.selenium.open('/portal/info/%s' % ob_id, True)
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)
        self._assert_view_page_ok()

    def _assert_view_page_ok(self):
        assert ("Test Object %s" % self.rnd) in self.selenium.get_text('//h1')

    def _add_glossary(self, glossary_id, xliff_name):
        from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
        manage_addGlossaryCentre(self.portal, glossary_id,
                                 "Glossary %s" % glossary_id)
        glossary = self.portal[glossary_id]
        xliff_file = open(path.join(fixtures_path, xliff_name), 'rb')
        glossary.xliff_import(xliff_file.read())
        xliff_file.close()

    def test_pick_keywords(self):
        #transaction.abort()
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
        self.selenium.type('keywords', u"")

        self.selenium.click("//input[@type='button'][@value='Pick']")
        self.selenium.wait_for_pop_up('pickkeyword',
                                      self._selenium_page_timeout)
        self.selenium.select_window('pickkeyword')
        self.selenium.click("//img[@alt='Expand']")
        # TODO wait for page to load?
        self.selenium.click("link=Shrubbery")
        self.selenium.click("link=Ni")
        self.selenium.close()
        self.selenium.select_window('')
        assert self.selenium.get_value("keywords") == 'Shrubbery, Ni'

        self.selenium.click("//input[@value='Submit']")
        self.selenium.wait_for_page_to_load(self._selenium_page_timeout)

        transaction.abort()
        ob = self.portal['info']['test-object-%s' % self.rnd]
        assert ob.keywords == "Shrubbery, Ni"

class FolderTest(_CommonContentTests):
    meta_label = "Folder"
    meta_type = "Naaya Folder"

    def add_object(self, parent, **kwargs):
        from Products.Naaya.NyFolder import addNyFolder
        return addNyFolder(parent, **kwargs)

    # Folders are allowed to have a blank title so, when running
    # test_edit_with_error, submit a blank value for "sort order".
    def _fill_edit_form_with_error(self):
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

#    def _get_image_container(self, ob):
#        return ob
#
    def add_object(self, parent, **kwargs):
        from naaya.content.story.story_item import addNyStory
        return addNyStory(parent, **kwargs)

class DocumentTest(_CommonContentTests):
    meta_label = "HTML Document"
    meta_type = "Naaya Document"

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

    def add_object(self, parent, **kwargs):
        from naaya.content.bfile.bfile_item import addNyBFile
        return addNyBFile(parent, **kwargs)

    def setUp(self):
        super(BlobFileTest, self).setUp()
        # "Naaya Blob File" is not installed by default
        self.portal.manage_uninstall_pluggableitem("Naaya File")
        self.portal.manage_install_pluggableitem("Naaya Blob File")
        self.portal.info.folder_meta_types += ["Naaya Blob File"]
        transaction.commit()

    def _assert_object_added_properly(self, container):
        super(BlobFileTest, self)._assert_object_added_properly(container)
        # make sure the right content type was added
        ob = container["test-object-%s" % self.rnd]
        assert ob.meta_type == "Naaya Blob File"

    def test_upload(self):
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
