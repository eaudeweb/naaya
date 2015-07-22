# Python
import time
from unittest import TestSuite, makeSuite
from BeautifulSoup import BeautifulSoup

# Zope
from DateTime import DateTime
import transaction

# Products
from Products.Naaya.NySite import NySite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya import NyFolder
from Products.Naaya.NyFolder import addNyFolder
from testNyFolder import FolderListingInfo

class TestNySite(NaayaTestCase):

    def afterSetUp(self):
        pass


    def beforeTearDown(self):
        pass
    
    
    def test_process_releasedate(self):
        """
        Test process_releasedate
        """
        now = DateTime()
        aDate = self.app.portal.process_releasedate("4/4/1978")
        self.assertEquals(aDate.year(), 1978, "Year was %s instead of 1978" % aDate.year())
        self.assertEquals(aDate.month(), 4, "Month was %s instead of 4" % aDate.month())
        self.assertEquals(aDate.day(), 4, "Day was %s instead of 4" % aDate.day())

        aDate = self.app.portal.process_releasedate("1978/4/30")
        self.assertEquals(aDate.year(), 1978, "Year was %s instead of 1978" % aDate.year())
        self.assertEquals(aDate.month(), 4, "Month was %s instead of 4" % aDate.month())
        self.assertEquals(aDate.day(), 30, "Day was %s instead of 30" % aDate.day())
        
        aDate = self.app.portal.process_releasedate()
        self.assertNotEquals(aDate, None)
        
        #If we pass a DateTime instance, fails :( 
        #TODO This can be improved by checking object type, if it's a DateTime
        #then simply return it
        now = DateTime()
        time.sleep(1)
        aDate = self.app.portal.process_releasedate(now)
        
        self.assertNotEqual(aDate, now, "The two dates were equal!")

class TestNySiteListing(NaayaFunctionalTestCase):
    """ """
    def afterSetUp(self):
        addNyFolder(self.portal, 'test_folder', contributor='contributor', submission=1)

        self.portal.getPortletsTool().assign_portlet('', 'center', 'portlet_objects_listing')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['test_folder'])

        self.portal.getPortletsTool().unassign_portlet('', 'center', 'portlet_objects_listing')
        transaction.commit()

    def test_view(self):
        self.browser_do_login('contributor', 'contributor')

        site_info = FolderListingInfo(self.browser, self.portal, 'test_folder')
        self.assertFalse(site_info.has_checkbox)
        self.assertTrue(site_info.has_index_link)
        self.assertTrue(site_info.has_edit_link)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNySite))
    suite.addTest(makeSuite(TestNySiteListing))
    return suite
