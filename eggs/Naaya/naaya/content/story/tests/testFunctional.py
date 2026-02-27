import re
from unittest import TestSuite, TestLoader
from bs4 import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyStoryFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.story.story_item import addNyStory
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyStory(self.portal.myfolder, id='mystory', title='My story', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/story_add')
        self.assertTrue('<h1>Submit Story</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:string', 'description:utf8:string', 'coverage:utf8:string',
            'keywords:utf8:string', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:string'] = 'test_story'
        form['description:utf8:string'] = 'test_story_description'
        form['coverage:utf8:string'] = 'test_story_coverage'
        form['keywords:utf8:string'] = 'keyw1, keyw2'
        form['body:utf8:string'] = 'test_story_body'

        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.info.test_story.approveThis()

        self.browser.go('http://localhost/portal/info/test_story')
        html = self.browser.get_html()
        self.assertTrue(re.search(r'<h1>.*test_story.*</h1>', html, re.DOTALL))
        self.assertTrue('test_story_description' in html)
        self.assertTrue('test_story_coverage' in html)
        self.assertTrue('keyw1, keyw2' in html)
        self.assertTrue('test_story_body' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/story_add')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mystory/edit_html')
        form = self.browser.get_form('frmEdit')

        self.assertEqual(form['title:utf8:string'], 'My story')

        form['title:utf8:string'] = 'new_story_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.mystory.title, 'new_story_title')

        self.browser.go('http://localhost/portal/myfolder/mystory/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:string'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.mystory.title, 'new_story_title')
        self.assertEqual(self.portal.myfolder.mystory.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mystory/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        form['title:utf8:string'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mystory/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['title:utf8:string'], 'My story')
        form['title:utf8:string'] = 'new_story_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.mystory.title, 'new_story_title')

        self.browser_do_logout()


    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html, "lxml")

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_story = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/mystory'})
        self.assertTrue(len(links_to_story) == 1)
        self.assertTrue(links_to_story[0].string == 'My story')

        self.browser_do_logout()

class NyStoryVersioningFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        from naaya.content.story.story_item import addNyStory
        addNyStory(self.portal.info, id='ver_story', title='ver_story', submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_story'])
        import transaction; transaction.commit()

    def test_start_version(self):
        from naaya.content.story.story_item import story_item
        self.browser_do_login('admin', '')
        self.assertEqual(self.portal.info.ver_story.version, None)
        self.browser.go('http://localhost/portal/info/ver_story/startVersion')
        self.assertTrue(isinstance(self.portal.info.ver_story.version, story_item))
        self.browser_do_logout()

    def test_edit_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_story/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:string'] = 'ver_story_newtitle'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        ver_story = self.portal.info.ver_story
        self.assertEqual(ver_story.title, 'ver_story')
        # we can't do ver_story.version.title because version objects don't have the _languages property
        self.assertEqual(ver_story.version.getLocalProperty('title', 'en'), 'ver_story_newtitle')

        self.browser_do_logout()

    def test_save_changes_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_story/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:string'] = 'ver_story_version'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()

        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['title:utf8:string'], 'ver_story_version')

        self.browser_do_logout()
