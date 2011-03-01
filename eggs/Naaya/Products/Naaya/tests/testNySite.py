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

    def _logged_mails(self):
        for entry_type, entry_data in self.mail_log:
            if entry_type == 'sendmail':
                yield entry_data

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

    def test_notify_on_errors(self):
        self.portal.notify_on_errors_email = 'errors@pivo.edw.ro'
        self.portal.error_log.setProperties(keep_entries=20, ignored_exceptions=('Unauthorized',))
        request = self.fake_request
        request['URL'] = 'http://localhost:8080/portal/test'

        # The Unauthorized error is listed in error_log.
        self.portal.processNotifyOnErrors(error_type='Unauthorized', error_value='You are not authorized to access this resource', REQUEST=request)
        sent_mails = list(self._logged_mails())
        self.assertEquals(len(sent_mails), 0)

        # The NotFound error is not listed in error_log. An email will be send.
        self.portal.processNotifyOnErrors(error_type='NotFound', error_value='Page is not found', REQUEST=request)
        sent_mails = list(self._logged_mails())
        self.assertEquals(len(sent_mails), 1)
        
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


class SearchPageFunctionalTest(NaayaFunctionalTestCase):
    def test_pagination(self):
        self.browser.go('http://localhost/portal/search_html?'
                        'query:utf8:ustring=accessibility&Naaya_Document=on')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        paginations = soup.findAll('div', attrs={'class': 'pagination'})
        self.assertEqual(len(paginations), 1)

        pagination = paginations[0]
        self.assertTrue('Showing page' in str(pagination))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNySite))
    suite.addTest(makeSuite(TestNySiteListing))
    return suite
