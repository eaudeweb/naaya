import time
from Products.Naaya.NySite import NySite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya import NyFolder
from unittest import TestSuite, makeSuite
from DateTime import DateTime

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


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNySite))
    return suite
