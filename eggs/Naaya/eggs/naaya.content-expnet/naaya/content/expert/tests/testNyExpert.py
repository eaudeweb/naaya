from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from naaya.content.expert import expert_item

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

def setUp_EW_data(portal):
    add_selection_list(portal, 'countries',
        dict((k,k) for k in ["Egypt", "Lybia", "Tunisia"]))

def tearDown_EW_data(portal):
    portal.portal_portlets.manage_delObjects(['countries'])

class TestNyExpert(NaayaTestCase):


    def afterSetUp(self):
        self.install_content_type('Naaya Expert')
        setUp_EW_data(self.portal)
        NyFolder.addNyFolder(self.app.portal, "test_folder")
        pass


    def beforeTearDown(self):
        self.app.portal.manage_delObjects("test_folder")
        tearDown_EW_data(self.portal)
        self.remove_content_type('Naaya Expert')


    def test_addNyExpert_nologin(self):
        """
        Test adding Expert without being logged in
        """
        expert_item.addNyExpert(self.app.portal.test_folder, name="Name", surname="Surname")
        self.assertFalse(hasattr(self.app.portal.test_folder, "Name"))
        


    def test_addNyExpert_no_requiredattrs(self):
        self.login("contributor")
        self.failUnlessRaises(ValueError, lambda: expert_item.addNyExpert(self.app.portal.test_folder))
        self.assertFalse(hasattr(self.app.portal.test_folder, "testExpert"))
        self.logout()


    def test_addNyExpert_has_requiredattrs(self):
        self.login("contributor")
        id = expert_item.addNyExpert(self.app.portal.test_folder, name="test1", surname="test1")
        self.assertTrue(hasattr(self.app.portal.test_folder, "test1-test1"), "Expert object test1-test1 was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya Expert"])
        test1 = None
        for expert in meta:
            if expert.title == "test1 test1":
                test1 = expert
        self.assertNotEqual(test1, None, "Expert not found via CatalogedObjectsCheckView")
        self.assertEqual(test1.title, "test1 test1")
        self.logout()


    def test_addNyExpert_duplicates(self):
        self.login("contributor")
        expert_item.addNyExpert(self.app.portal.test_folder, id="expertdup1", name="expertdup1", surname="expertdup1")
        self.assertTrue(hasattr(self.app.portal.test_folder, "expertdup1"), "Expert object expertdup1 was not found in folder 'test_folder'")
        expert_item.addNyExpert(self.app.portal.test_folder, id="expertdup1", name="expertdup1", surname="expertdup1")
        self.assertTrue(hasattr(self.app.portal.test_folder, "expertdup1-1"), "Expert object expertdup1 was not found in folder 'test_folder'")
        self.logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyExpert))
    return suite
