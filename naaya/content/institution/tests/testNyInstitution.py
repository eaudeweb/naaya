from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from naaya.content.institution import institution_item

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

class TestNyInstitution(NaayaTestCase):


    def afterSetUp(self):
        self.install_content_type('Naaya Institution')
        setUp_EW_test_data(self.portal)
        NyFolder.addNyFolder(self.app.portal, "test_folder")
        pass


    def beforeTearDown(self):
        self.app.portal.manage_delObjects("test_folder")
        tearDown_EW_test_data(self.portal)
        self.remove_content_type('Naaya Institution')


    def test_addNyInstitution_nologin(self):
        """
        Test adding Institution without being logged in
        """
        institution_item.addNyInstitution(self.app.portal.test_folder, title="My institution")
        self.assertFalse(hasattr(self.app.portal.test_folder, "My institution"))
        


    def test_addNyInstitution_no_requiredattrs(self):
        self.login("contributor")
        self.failUnlessRaises(ValueError, lambda: institution_item.addNyInstitution(self.app.portal.test_folder))
        self.assertFalse(hasattr(self.app.portal.test_folder, "testInstitution"))
        self.logout()


    def test_addNyInstitution_has_requiredattrs(self):
        self.login("contributor")
        id = institution_item.addNyInstitution(self.app.portal.test_folder, title="Test Institution")
        self.assertTrue(hasattr(self.app.portal.test_folder, "test-institution"), "Institution object Test Institution was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya Institution"])
        test1 = None
        for institution in meta:
            if institution.title == "Test Institution":
                test1 = institution
        self.assertNotEqual(test1, None, "Institution not found via CatalogedObjectsCheckView")
        self.assertEqual(test1.title, "Test Institution")
        self.logout()


    def test_addNyInstitution_duplicates(self):
        self.login("contributor")
        institution_item.addNyInstitution(self.app.portal.test_folder, id="institution", title="Institution")
        self.assertTrue(hasattr(self.app.portal.test_folder, "institution"), "Institution object institution was not found in folder 'test_folder'")
        institution_item.addNyInstitution(self.app.portal.test_folder, id="institution", title="Institution")
        self.assertTrue(hasattr(self.app.portal.test_folder, "institution-1"), "Institution object institution was not found in folder 'test_folder'")
        self.logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyInstitution))
    return suite
