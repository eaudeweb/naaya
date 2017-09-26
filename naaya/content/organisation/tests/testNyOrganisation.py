from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from naaya.content.organisation import organisation_item

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

class TestNyOrganisation(NaayaTestCase):


    def afterSetUp(self):
        self.install_content_type('Naaya Organisation')
        setUp_EW_data(self.portal)
        NyFolder.addNyFolder(self.app.portal, "test_folder")
        pass


    def beforeTearDown(self):
        self.app.portal.manage_delObjects("test_folder")
        tearDown_EW_data(self.portal)
        self.remove_content_type('Naaya Organisation')


    def test_addNyOrganisation_nologin(self):
        """
        Test adding Organisation without being logged in
        """
        organisation_item.addNyOrganisation(self.app.portal.test_folder, title="My organisation")
        self.assertFalse(hasattr(self.app.portal.test_folder, "My organisation"))
        


    def test_addNyOrganisation_no_requiredattrs(self):
        self.login("contributor")
        self.failUnlessRaises(ValueError, lambda: organisation_item.addNyOrganisation(self.app.portal.test_folder))
        self.assertFalse(hasattr(self.app.portal.test_folder, "testOrganisation"))
        self.logout()


    def test_addNyOrganisation_has_requiredattrs(self):
        self.login("contributor")
        id = organisation_item.addNyOrganisation(self.app.portal.test_folder, title="Test Organisation")
        self.assertTrue(hasattr(self.app.portal.test_folder, "test-organisation"), "Organisation object Test Organisation was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya Organisation"])
        test1 = None
        for organisation in meta:
            if organisation.title == "Test Organisation":
                test1 = organisation
        self.assertNotEqual(test1, None, "Organisation not found via CatalogedObjectsCheckView")
        self.assertEqual(test1.title, "Test Organisation")
        self.logout()


    def test_addNyOrganisation_duplicates(self):
        self.login("contributor")
        organisation_item.addNyOrganisation(self.app.portal.test_folder, id="organisation", title="Organisation")
        self.assertTrue(hasattr(self.app.portal.test_folder, "organisation"), "Organisation object organisation was not found in folder 'test_folder'")
        organisation_item.addNyOrganisation(self.app.portal.test_folder, id="organisation", title="Organisation")
        self.assertTrue(hasattr(self.app.portal.test_folder, "organisation-1"), "Organisation object organisation was not found in folder 'test_folder'")
        self.logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyOrganisation))
    return suite
