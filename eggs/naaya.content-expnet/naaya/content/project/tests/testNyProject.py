from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from naaya.content.project import project_item

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

class TestNyProject(NaayaTestCase):


    def afterSetUp(self):
        self.install_content_type('Naaya Project')
        NyFolder.addNyFolder(self.app.portal, "test_folder")
        pass


    def beforeTearDown(self):
        self.app.portal.manage_delObjects("test_folder")
        self.remove_content_type('Naaya Project')


    def test_addNyProject_nologin(self):
        """
        Test adding Project without being logged in
        """
        project_item.addNyProject(self.app.portal.test_folder, title="Title")
        self.assertFalse(hasattr(self.app.portal.test_folder, "Title"))
        


    def test_addNyProject_no_requiredattrs(self):
        self.login("contributor")
        self.failUnlessRaises(ValueError, lambda: project_item.addNyProject(self.app.portal.test_folder))
        self.assertFalse(hasattr(self.app.portal.test_folder, "testProject"))
        self.logout()


    def test_addNyProject_has_requiredattrs(self):
        self.login("contributor")
        id = project_item.addNyProject(self.app.portal.test_folder, title="test1")
        self.assertTrue(hasattr(self.app.portal.test_folder, "test1"), "Project object test1-test1 was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya Project"])
        test1 = None
        for project in meta:
            if project.title == "test1":
                test1 = project
        self.assertNotEqual(test1, None, "Project not found via CatalogedObjectsCheckView")
        self.assertEqual(test1.title, "test1")
        self.logout()


    def test_addNyProject_duplicates(self):
        self.login("contributor")
        project_item.addNyProject(self.app.portal.test_folder, id="projectdup1", title="projectdup1")
        self.assertTrue(hasattr(self.app.portal.test_folder, "projectdup1"), "Project object projectdup1 was not found in folder 'test_folder'")
        project_item.addNyProject(self.app.portal.test_folder, id="projectdup1", title="projectdup1")
        self.assertTrue(hasattr(self.app.portal.test_folder, "projectdup1-1"), "Project object projectdup1 was not found in folder 'test_folder'")
        self.logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyProject))
    return suite
