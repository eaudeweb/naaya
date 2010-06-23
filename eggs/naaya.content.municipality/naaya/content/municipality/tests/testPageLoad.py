from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.expert.expert_item import addNyExpert

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

def setUp_EW_test_data(portal):
    add_selection_list(portal, 'countries',
        dict((k,k) for k in ["Egypt", "Lybia", "Tunisia"]))

def tearDown_EW_test_data(portal):
    portal.portal_portlets.manage_delObjects(['countries'])

class PageLoadTests(NaayaTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya Expert')
        setUp_EW_test_data(self.portal)
        portal = self.app.portal
        addNyFolder(portal, 'test_folder')
        addNyExpert(portal.test_folder, id='test_expert', name='test_expert', surname="And his surname")

    def beforeTearDown(self):
        self.app.portal.test_folder.manage_delObjects('test_expert')
        self.app.portal.manage_delObjects('test_folder')
        tearDown_EW_test_data(self.portal)
        self.remove_content_type('Naaya Expert')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_expert = self.app.portal.test_folder.test_expert

        test_folder.expert_add_html()
        test_expert.index_html()
        test_expert.edit_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
