"""The TinyMCE editor and the folder listing actions in Chromium."""
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.BrowserTestCase import BrowserTestCase
from naaya.content.news.news_item import addNyNews


class EditorBrowserTest(BrowserTestCase):

    def afterSetUp(self):
        addNyFolder(self.portal, 'uifolder', contributor='admin', submitted=1)
        self.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['uifolder'])
        self.commit()

    def test_add_news_with_the_editor(self):
        self.login()
        self.page.goto(self.url('uifolder/news_add_html'))
        self.page.wait_for_function(
            'window.tinymce && tinymce.activeEditor && tinymce.activeEditor.initialized')
        self.page.fill('input[name="title:utf8:string"]', 'Editor news')
        body = self.page.frame_locator('#details_ifr').locator('body')
        body.click()
        body.type('Typed in the editor')
        self.page.click('form[name="frmAdd"] input[type="submit"][value="Submit"]')
        self.page.wait_for_load_state()
        self.portal._p_jar.sync()
        news = self.portal.uifolder.objectValues(['Naaya News'])
        self.assertEqual(len(news), 1)
        self.assertIn('Typed in the editor', news[0].details)
        self.assertEqual(self.js_errors, [])


class FolderListingBrowserTest(BrowserTestCase):

    def afterSetUp(self):
        addNyFolder(self.portal, 'listfolder', contributor='admin', submitted=1)
        for ob_id in ('keep', 'remove'):
            addNyNews(self.portal.listfolder, id=ob_id, title=ob_id, submitted=1,
                      contributor='admin')
        self.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['listfolder'])
        self.commit()

    def test_delete_selected_item(self):
        self.login()
        self.page.goto(self.url('listfolder'))
        self.page.check('#folderfile_list input[type="checkbox"][value="remove"]')
        self.page.click('input[name="deleteObjects:method"]')
        self.page.click('.ui-dialog-buttonpane button:has-text("Delete items")')
        self.page.wait_for_load_state()
        self.page.wait_for_selector('#folderfile_list')
        self.portal._p_jar.sync()
        self.assertEqual(sorted(self.portal.listfolder.objectIds()), ['keep'])
        self.assertEqual(self.js_errors, [])

    def test_delete_without_selection_alerts(self):
        self.login()
        self.page.goto(self.url('listfolder'))
        messages = []
        self.page.on('dialog', lambda dialog: (messages.append(dialog.message), dialog.accept()))
        self.page.click('input[name="deleteObjects:method"]')
        self.page.wait_for_function('true')
        self.assertEqual(len(messages), 1)
        self.portal._p_jar.sync()
        self.assertEqual(sorted(self.portal.listfolder.objectIds()), ['keep', 'remove'])
