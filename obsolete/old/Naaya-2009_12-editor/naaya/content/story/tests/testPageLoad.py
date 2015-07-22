from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.story.story_item import addNyStory

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyStory(portal.test_folder, id='test_story', title='test story')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_story')
        self.app.portal.manage_delObjects('test_folder')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_story = self.app.portal.test_folder.test_story

        test_story.index_html()
        test_story.edit_html()
        test_story.add_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
