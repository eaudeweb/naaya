from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.project.project_item import addNyProject

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

class PageLoadTests(NaayaTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya Project')
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyProject(portal.test_folder, id='test_project', title='test_project')

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_project')
        self.app.portal.manage_delObjects('test_folder')
        self.remove_content_type('Naaya Project')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_project = self.app.portal.test_folder.test_project

        test_folder.project_add_html()
        test_project.index_html()
        test_project.edit_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
