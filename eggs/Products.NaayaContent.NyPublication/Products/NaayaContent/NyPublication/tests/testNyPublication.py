from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from Products.NaayaContent.NyPublication import NyPublication

class TestNyPublication(NaayaTestCase):


    def afterSetUp(self):
        NyFolder.addNyFolder(self.app.portal, "test_folder")
        pass


    def beforeTearDown(self):
        self.app.portal.manage_delObjects("test_folder")


    def test_addNyPublication_nologin(self):
        """
        Test adding Publication without being logged in
        """
        NyPublication.addNyPublication(self.app.portal.test_folder, title="testPublication")
        self.assertFalse(hasattr(self.app.portal.test_folder, "testPublication"))
        


    def test_addNyPublication_no_requiredattrs(self):
        self.login("contributor")
        self.failUnlessRaises(ValueError, lambda: NyPublication.addNyPublication(self.app.portal.test_folder))
        self.assertFalse(hasattr(self.app.portal.test_folder, "testPublication"))
        self.logout()


    def test_addNyPublication_has_requiredattrs(self):
        self.login("contributor")
        id = NyPublication.addNyPublication(self.app.portal.test_folder, title="test1", locator="www.google.com")
        self.assertTrue(hasattr(self.app.portal.test_folder, "test1"), "Publication object test1 was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya Publication"])
        test1 = None
        for pub in meta:
            if pub.title == "test1":
                test1 = pub
        self.assertNotEqual(test1, None, "Publication not found via CatalogedObjectsCheckView")
        self.assertEqual(test1.title, "test1")
        self.assertEqual(test1.locator, "www.google.com")
        self.logout()


    def test_addNyPublication_duplicates(self):
        self.login("contributor")
        NyPublication.addNyPublication(self.app.portal.test_folder, id="pubdup1", title="pubdup1", locator="www.google.com")
        self.assertTrue(hasattr(self.app.portal.test_folder, "pubdup1"), "Publication object pubdup1 was not found in folder 'test_folder'")
        NyPublication.addNyPublication(self.app.portal.test_folder, id="pubdup1", title="pubdup1", locator="www.google.com")
        self.assertTrue(hasattr(self.app.portal.test_folder, "pubdup1-1"), "Publication object pubdup1 was not found in folder 'test_folder'")
        self.logout()


    def test_addNyPublication_fullattrs(self):
        import time
        self.login("contributor")
        time.sleep(1)
        NyPublication.addNyPublication(self.app.portal.test_folder,
                            id="test2", 
                            title="test2", 
                            description = "description",
                            coverage = "coverage",
                            keywords = "keyword1, keywords2",
                            sortorder = 1,
                            locator="www.google.com",
                            contributor = "cristiroma",
                            releasedate = "30/04/2008",
                            discussion = 1,
                            lang = "ar"
                            )
        self.assertTrue(hasattr(self.app.portal.test_folder, "test2"), "Publication object test2 was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya Publication"])
        test2 = None
        for pub in meta:
            if pub.getLocalProperty("title", "ar") == "test2":
                test2 = pub
        self.assertTrue(test2 != None, "Publication not found via CatalogedObjectsCheckView")
        self.assertEqual(test2.id(), "test2")
        self.assertEqual(test2.getLocalProperty("title", "ar"), "test2")
        self.assertEqual(test2.getLocalProperty("description", "ar"), "description")
        self.assertEqual(test2.getLocalProperty("coverage", "ar"), "coverage")
        self.assertEqual(test2.getLocalProperty("keywords", "ar"), "keyword1, keywords2")
        self.assertEqual(test2.sortorder, 1)
        self.assertEqual(test2.getLocalProperty("locator", "ar"), "www.google.com")
        self.assertEqual(test2.contributor, "cristiroma")
        self.assertEqual(test2.releasedate.day(), 30, "Release day does not match")
        self.assertEqual(test2.releasedate.month(), 4, "Release month does not match")
        self.assertEqual(test2.releasedate.year(), 2008, "Release year does not match")
        self.assertEqual(test2.discussion, 1)
        self.logout()


    def test_importNyPublication(self):
        attrs = {"sortorder" : "1", 
                  "contributor" : "contributor", 
                  "discussion" : "1", 
                  "approved" : "1",
                  "approved_by" : "contributor",
                  "releasedate" : "30/04/2008",
                  "validation_status" : "None",
                  "validation_comment" : "OK",
                  "validation_by" : "contributor",
                  "validation_date" : "30/04/2008"}
        id = "pub3"
        param = 0;
        
        self.app.portal.test_folder.importNyPublication(param, id, attrs, '', {}, None, None)
        self.assertTrue(hasattr(self.app.portal.test_folder, "pub3"), "Publication object pub3 was not found in folder 'test_folder'")


    def test_export_this_tag_custom(self):
        import re
        self.login("contributor")
        NyPublication.addNyPublication(self.app.portal.test_folder, title="pubx", contributor="cristiroma", locator="www.google.com")
        pub = self.app.portal.test_folder.pubx
        self.app.portal.test_folder.validateObject(id="pubx", status="-1", comment="No comment")
        exportStr = pub.export_this_tag_custom()
        strre=re.compile(exportStr, re.IGNORECASE)
        self.assertTrue(exportStr.find('validation_status="-1"') >= 0, "Exported custom tag is malformed")
        #TODO: self.assertTrue(strre.search('validation_date') != None, "Exported custom tag is malformed")
        self.assertTrue(exportStr.find('validation_by="contributor"') >= 0, "Exported custom tag is malformed")
        self.assertTrue(exportStr.find('validation_comment="No comment"') >= 0, "Exported custom tag is malformed")
        
        self.logout()


    def test_export_this_body_custom(self):
        self.login("contributor")
        NyPublication.addNyPublication(self.app.portal.test_folder, title="puby", contributor="cristiroma", locator="www.google.com")
        pub = self.app.portal.test_folder.puby
        exportStr = pub.export_this_body_custom()
        self.assertTrue(exportStr == '<locator lang="en"><![CDATA[www.google.com]]></locator>', "Exported custom body is malformed")
        self.logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyPublication))
    return suite
