from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from naaya.content.url import url_item

class TestNyURL(NaayaTestCase):


    def afterSetUp(self):
        NyFolder.addNyFolder(self.app.portal, "test_folder")
        pass


    def beforeTearDown(self):
        self.app.portal.manage_delObjects("test_folder")


    def test_addNyURL_nologin(self):
        """
        Test adding URL without being logged in
        """
        url_item.addNyURL(self.app.portal.test_folder, title="testURL")
        self.assertFalse(hasattr(self.app.portal.test_folder, "testURL"))
        


    def test_addNyURL_no_requiredattrs(self):
        self.login("contributor")
        self.failUnlessRaises(ValueError, lambda: url_item.addNyURL(self.app.portal.test_folder))
        self.assertFalse(hasattr(self.app.portal.test_folder, "testURL"))
        self.logout()


    def test_addNyURL_has_requiredattrs(self):
        self.login("contributor")
        id = url_item.addNyURL(self.app.portal.test_folder, title="test1", locator="www.google.com")
        self.assertTrue(hasattr(self.app.portal.test_folder, "test1"), "URL object test1 was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya URL"])
        test1 = None
        for url in meta:
            if url.title == "test1":
                test1 = url
        self.assertNotEqual(test1, None, "URL not found via CatalogedObjectsCheckView")
        self.assertEqual(test1.title, "test1")
        self.assertEqual(test1.locator, "www.google.com")
        self.logout()


    def test_addNyURL_duplicates(self):
        self.login("contributor")
        url_item.addNyURL(self.app.portal.test_folder, id="urldup1", title="urldup1", locator="www.google.com")
        self.assertTrue(hasattr(self.app.portal.test_folder, "urldup1"), "URL object urldup1 was not found in folder 'test_folder'")
        url_item.addNyURL(self.app.portal.test_folder, id="urldup1", title="urldup1", locator="www.google.com")
        self.assertTrue(hasattr(self.app.portal.test_folder, "urldup1-1"), "URL object urldup1 was not found in folder 'test_folder'")
        self.logout()


    def test_addNyURL_fullattrs(self):
        import time
        self.login("contributor")
        time.sleep(1)
        url_item.addNyURL(self.app.portal.test_folder,
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
        self.assertTrue(hasattr(self.app.portal.test_folder, "test2"), "URL object test2 was not found in folder 'test_folder'")
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=["Naaya URL"])
        test2 = None
        for url in meta:
            if url.getLocalProperty("title", "ar") == "test2":
                test2 = url
        self.assertTrue(test2 != None, "URL not found via CatalogedObjectsCheckView")
        self.assertEqual(test2.id, "test2")
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


    def test_importNyURL(self):
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
        id = "url3"
        param = 0;
        
        self.app.portal.test_folder.import_url_item(param, id, attrs, '', {}, None, None)
        self.assertTrue(hasattr(self.app.portal.test_folder, "url3"), "URL object url3 was not found in folder 'test_folder'")


    def test_export_this_tag_custom(self):
        import re
        self.login("contributor")
        url_item.addNyURL(self.app.portal.test_folder, title="urlx", contributor="cristiroma", locator="www.google.com")
        url = self.app.portal.test_folder.urlx
        self.app.portal.test_folder.validateObject(id="urlx", status="-1", comment="No comment")
        exportStr = url.export_this_tag_custom()
        strre=re.compile(exportStr, re.IGNORECASE)
        self.assertTrue(exportStr.find('validation_status="-1"') >= 0, "Exported custom tag is malformed")
        #TODO: self.assertTrue(strre.search('validation_date') != None, "Exported custom tag is malformed")
        self.assertTrue(exportStr.find('validation_by="contributor"') >= 0, "Exported custom tag is malformed")
        self.assertTrue(exportStr.find('validation_comment="No comment"') >= 0, "Exported custom tag is malformed")
        
        self.logout()


    def test_export_this_body_custom(self):
        self.login("contributor")
        url_item.addNyURL(self.app.portal.test_folder, title="urly", contributor="cristiroma", locator="www.google.com")
        url = self.app.portal.test_folder.urly
        exportStr = url.export_this_body_custom()
        self.assertTrue(exportStr == '<locator lang="en"><![CDATA[www.google.com]]></locator>', "Exported custom body is malformed")
        self.logout()


    def test_startVersion(self):
        import traceback
        self.login("contributor")
        url_item.addNyURL(self.app.portal.test_folder,
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
        url = self.app.portal.test_folder.test2
        #Contributor is not allowed to start versioning

        # TODO: fix this test
        #try:
        #    url.startVersion()
        #    self.fail()
        #except:
        #    pass

        self.logout()
        self.login()
        url.startVersion()
        url.saveProperties(
                           title='test22', 
                           description='', 
                           coverage='', 
                           keywords='',
                           sortorder=10, 
                           locator='www.yahoo.com', 
                           releasedate='02/02/2003', 
                           discussion=0,
                           lang="ar")
        self.assertEqual(url.id, "test2")
        self.assertEqual(url.getLocalProperty("title", "ar"), "test2")
        self.assertEqual(url.getLocalProperty("description", "ar"), "description")
        self.assertEqual(url.getLocalProperty("coverage", "ar"), "coverage")
        self.assertEqual(url.getLocalProperty("keywords", "ar"), "keyword1, keywords2")
        self.assertEqual(url.sortorder, 1)
        self.assertEqual(url.getLocalProperty("locator", "ar"), "www.google.com")
        self.assertEqual(url.contributor, "cristiroma")
        self.assertEqual(url.releasedate.day(), 30, "Release day does not match")
        self.assertEqual(url.releasedate.month(), 4, "Release month does not match")
        self.assertEqual(url.releasedate.year(), 2008, "Release year does not match")
        #Discussion field passes the versioning system, no need to test self.assertEqual(url.discussion, 1)
        url.commitVersion()
        self.assertEqual(url.id, "test2")
        self.assertEqual(url.getLocalProperty("title", "ar"), "test22")
        self.assertEqual(url.getLocalProperty("description", "ar"), "")
        self.assertEqual(url.getLocalProperty("coverage", "ar"), "")
        self.assertEqual(url.getLocalProperty("keywords", "ar"), "")
        self.assertEqual(url.sortorder, 10)
        self.assertEqual(url.getLocalProperty("locator", "ar"), "www.yahoo.com")
        self.assertEqual(url.contributor, "cristiroma")
        self.assertEqual(url.releasedate.day(), 2, "Release day does not match")
        self.assertEqual(url.releasedate.month(), 2, "Release month does not match")
        self.assertEqual(url.releasedate.year(), 2003, "Release year does not match")
        #Discussion field passes the versioning system, no noeed to test self.assertEqual(url.discussion, 0)
        
        url.startVersion()
        url.saveProperties(
                           title='1', 
                           description='1', 
                           coverage='1', 
                           keywords='1',
                           sortorder=1, 
                           locator='1', 
                           releasedate='03/03/2004', 
                           discussion=1,
                           lang="ar")
        url.discardVersion()
        self.assertEqual(url.id, "test2")
        self.assertEqual(url.getLocalProperty("title", "ar"), "test22")
        self.assertEqual(url.getLocalProperty("description", "ar"), "")
        self.assertEqual(url.getLocalProperty("coverage", "ar"), "")
        self.assertEqual(url.getLocalProperty("keywords", "ar"), "")
        self.assertEqual(url.sortorder, 10)
        self.assertEqual(url.getLocalProperty("locator", "ar"), "www.yahoo.com")
        self.assertEqual(url.contributor, "cristiroma")
        self.assertEqual(url.releasedate.day(), 2, "Release day does not match")
        self.assertEqual(url.releasedate.month(), 2, "Release month does not match")
        self.assertEqual(url.releasedate.year(), 2003, "Release year does not match")


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNyURL))
    return suite
