# Python
import time
from BeautifulSoup import BeautifulSoup
from mock import patch

# Zope
from DateTime import DateTime
import transaction
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

# Products
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
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
        self.assertEquals(aDate.year(), 1978,
                          "Year was %s instead of 1978" % aDate.year())
        self.assertEquals(aDate.month(), 4,
                          "Month was %s instead of 4" % aDate.month())
        self.assertEquals(aDate.day(), 4,
                          "Day was %s instead of 4" % aDate.day())

        aDate = self.app.portal.process_releasedate("1978/4/30")
        self.assertEquals(aDate.year(), 1978,
                          "Year was %s instead of 1978" % aDate.year())
        self.assertEquals(aDate.month(), 4,
                          "Month was %s instead of 4" % aDate.month())
        self.assertEquals(aDate.day(), 30,
                          "Day was %s instead of 30" % aDate.day())

        aDate = self.app.portal.process_releasedate()
        self.assertNotEquals(aDate, None)

        #If we pass a DateTime instance, fails :(
        #TODO This can be improved by checking object type, if it's a DateTime
        #then simply return it
        now = DateTime()
        time.sleep(1)
        aDate = self.app.portal.process_releasedate(now)

        self.assertNotEqual(aDate, now, "The two dates were equal!")

    @patch('Products.NaayaCore.EmailTool.EmailTool'
           '.EmailTool.sendEmailImmediately')
    def test_notify_on_errors(self, mock_send_mail):
        self.portal.notify_on_errors_email = 'errors@pivo.edw.ro'
        error_log = self.portal.error_log
        error_log.setProperties(keep_entries=20,
                                ignored_exceptions=('Unauthorized',))
        request = self.fake_request
        request['URL'] = 'http://localhost:8080/portal/test'

        # The Unauthorized error is listed in error_log.
        self.portal.processNotifyOnErrors(error_type='Unauthorized',
                error_value='You are not authorized to access this resource',
                REQUEST=request)
        self.assertEqual(mock_send_mail.call_count, 0)

        # The NotFound error is not listed in error_log. An email will be send.
        self.portal.processNotifyOnErrors(error_type='NotFound',
                                          error_value='Page is not found',
                                          REQUEST=request)
        self.assertEqual(mock_send_mail.call_count, 1)


class TestNySiteListing(NaayaFunctionalTestCase):
    """ """
    def afterSetUp(self):
        addNyFolder(self.portal, 'test_folder', contributor='contributor',
                    submission=1)

        portlets_tool = self.portal.getPortletsTool()
        portlets_tool.assign_portlet('', 'center', 'portlet_objects_listing')

        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['test_folder'])

        portlets_tool = self.portal.getPortletsTool()
        portlets_tool.unassign_portlet('', 'center', 'portlet_objects_listing')

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


class SiteIndexInLayoutTest(NaayaFunctionalTestCase):
    TEXT = '__layout_site_index__'

    def setUp(self):
        super(SiteIndexInLayoutTest, self).setUp()

        layout_tool = self.portal.getLayoutTool()
        current_skin = layout_tool.get_current_skin()

        if hasattr(current_skin, 'site_index'):
            current_skin.site_index.write(self.TEXT)
        else:
            manage_addPageTemplate(current_skin, 'site_index', text=self.TEXT)

        transaction.commit()

    def test_site_index_text(self):
        self.browser.go('http://localhost/portal')
        html = self.browser.get_html()
        self.assertEqual(html.strip(), self.TEXT)


class SiteIndexNotInLayoutTest(NaayaFunctionalTestCase):
    TEXT = '__forms_site_index__'

    def setUp(self):
        super(SiteIndexNotInLayoutTest, self).setUp()

        forms_tool = self.portal.getFormsTool()
        layout_tool = self.portal.getLayoutTool()
        current_skin = layout_tool.get_current_skin()

        if hasattr(current_skin, 'site_index'):
            current_skin.manage_delObjects(['site_index'])

        if hasattr(forms_tool, 'site_index'):
            forms_tool.site_index.write(self.TEXT)
        else:
            manage_addPageTemplate(forms_tool, 'site_index', text=self.TEXT)

        transaction.commit()

    def test_site_index_text(self):
        self.browser.go('http://localhost/portal')
        html = self.browser.get_html()
        self.assertEqual(html.strip(), self.TEXT)

class TestNySiteOFS(NaayaFunctionalTestCase):
    """Perform OFS operations (copy/cut/paste/delete) on `INySite` objects"""

    def afterSetUp(self):
        #Add basic auth credentials so we can access the ZMI
        self.browser.creds.add_password('Zope',
            self.portal.aq_parent.absolute_url(), 'admin', '')

    def _paste(self):
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'manage_pasteObjects:method')
        self.browser.clicked(form, field)
        self.browser.submit()

    def test_copypaste(self):
        """ `Copy` & `Paste`"""
        self.browser.go(self.portal.aq_parent.absolute_url() +
                        '/manage_main/')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'manage_copyObjects:method')
        self.browser.clicked(form, field)
        form['ids:list'] = ['portal']
        self.browser.submit()

        self._paste()
        self.assertTrue('copy_of_portal' in self.browser.get_html())

    def test_cutpaste(self):
        """ `Cut` & `Paste` """

        self.browser.go(self.portal.aq_parent.absolute_url() +
                        '/manage_main/')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'manage_cutObjects:method')
        self.browser.clicked(form, field)
        form['ids:list'] = ['portal']
        self.browser.submit()

        self._paste()
        self.assertTrue('portal' in self.browser.get_html())

    def test_delete(self):
        """ `Delete` button """
        self.browser.go(self.portal.aq_parent.absolute_url() +
                        '/manage_main/')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'manage_delObjects:method')
        self.browser.clicked(form, field)
        form['ids:list'] = ['portal']
        self.browser.submit()
        self.assertTrue('portal' not in self.browser.get_html())

    def test_copypaste_before_traverse(self):
        """ `Copy` & `Paste` and test that __before_traverse__ is changed """
        self.test_copypaste()

        old_traverse = self.portal.__before_traverse__
        new_traverse = self.portal.aq_parent.copy_of_portal.__before_traverse__

        for key in old_traverse.keys():
            if key not in new_traverse: #Some keys should be modified
                break
        else:
            raise ValueError("Same __before_traverse__ as in original portal")
