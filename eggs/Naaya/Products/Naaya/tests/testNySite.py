import time
import unittest
from BeautifulSoup import BeautifulSoup
from mock import patch, Mock
try:
    import simplejson as json
except ImportError:
    import json

from DateTime import DateTime
import transaction
from Products.PageTemplates.ZopePageTemplate import (ZopePageTemplate,
        manage_addPageTemplate)
from AccessControl.Permissions import view
from AccessControl.Permission import Permission

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.FormsTool.interfaces import ITemplate
from Products.Naaya.NySite import manage_addNySite, NySite

from zope.interface import alsoProvides
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
        self.portal.REQUEST = request

        # The Unauthorized error is listed in error_log.
        self.portal.standard_error_message(error_type='Unauthorized',
                error_value='You are not authorized to access this resource')
        self.assertEqual(mock_send_mail.call_count, 0)

        # The NotFound error is not listed in error_log. An email will be send.
        self.portal.standard_error_message(error_type='NotFound',
                                           error_value='Page is not found')
        self.assertEqual(mock_send_mail.call_count, 1)

    def test_list_permissions(self):
        perms = self.portal.get_naaya_permissions_in_site()
        skip_captcha = 'Naaya - Skip Captcha'
        self.assertTrue(skip_captcha in perms.keys())
        self.assertTrue('Naaya - Add Naaya URL objects' in perms.keys())
        self.assertEqual(perms[skip_captcha]['zope_permission'], skip_captcha)
        self.assertTrue('title' in perms[skip_captcha].keys())
        self.assertTrue('description' in perms[skip_captcha].keys())

    def test_view_permission_not_inherited(self):
        view_perm = Permission(view, (), self.portal)
        site_roles_with_view = view_perm.getRoles()
        self.assertTrue(tuple is type(site_roles_with_view))


class NoPermissionsForAnonymous(NaayaFunctionalTestCase):
    def setUp(self):
        super(NoPermissionsForAnonymous, self).setUp()
        self.portal.admin_editrole('Anonymous', [])
        transaction.commit()

    def test_anonymous_can_have_view_restricted(self):
        self.browser.go(self.portal.absolute_url())
        self.assertNotEqual(self.portal.absolute_url(), self.browser.get_url())


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

        form_ob = ZopePageTemplate('site_index', text=self.TEXT)
        alsoProvides(form_ob, ITemplate)
        forms_tool._setObject('site_index', form_ob)

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


class NavigationSiteMapTest(NaayaTestCase):

    def t(self, node):
        """ just a shorter method to grab node title """
        return node['attributes']['title']

    def setUp(self):
        super(NaayaTestCase, self).setUp()
        self.req = Mock()
        addNyFolder(self.portal.info, 'sub_approved', submitted=1,
                    contributor='contributor')
        self.portal.info.sub_approved.approved = True
        addNyFolder(self.portal.info, 'sub_unapproved', submitted=1,
                    contributor='contributor')

    def test_json_root(self):
        t = self.t
        self.req.form = {'node': '/'}

        res = json.loads(self.portal.getNavigationSiteMap(self.req))
        self.assertEqual(t(res), '')
        self.assertEqual(len(res['children']), 1)
        self.assertEqual(t(res['children'][0]), 'info')
        self.assertEqual(t(res['children'][0]['children'][1]), 'info/cookie_policy')
        self.assertEqual(res['children'][0]['children'][1]['children'], [])
        self.assertEqual(t(res['children'][0]['children'][2]), 'info/contact')

        res = json.loads(self.portal.getNavigationSiteMap(self.req, all=True))
        self.assertEqual(t(res), '')
        self.assertEqual(t(res['children'][0]), 'info')
        self.assertEqual(t(res['children'][0]['children'][1]), 'info/cookie_policy')
        self.assertEqual(t(res['children'][0]['children'][2]), 'info/contact')
        self.assertEqual(t(res['children'][0]['children'][3]), 'info/sub_approved')
        self.assertEqual(t(res['children'][0]['children'][4]), 'info/sub_unapproved')
        self.assertEqual(res['children'][0]['children'][3]['children'], [])

        res = json.loads(self.portal.getNavigationSiteMap(self.req, only_folders=True))
        self.assertEqual(t(res), '')
        self.assertEqual(t(res['children'][0]), 'info')
        self.assertEqual(len(res['children'][0]['children']), 1)
        self.assertEqual(t(res['children'][0]['children'][0]), 'info/sub_approved')

    def test_json_node(self):
        t = self.t
        self.req.form = {'node': 'info'}

        res = json.loads(self.portal.getNavigationSiteMap(self.req))
        self.assertEqual(len(res), 4)
        self.assertEqual(t(res[0]), 'info/accessibility')
        self.assertEqual(t(res[1]), 'info/cookie_policy')
        self.assertEqual(t(res[2]), 'info/contact')
        self.assertEqual(t(res[3]), 'info/sub_approved')

        res = json.loads(self.portal.getNavigationSiteMap(self.req, all=True))
        self.assertEqual(len(res), 5)
        self.assertEqual(t(res[0]), 'info/accessibility')
        self.assertEqual(t(res[1]), 'info/cookie_policy')
        self.assertEqual(t(res[2]), 'info/contact')
        self.assertEqual(t(res[3]), 'info/sub_approved')
        self.assertEqual(t(res[4]), 'info/sub_unapproved')

        res = json.loads(self.portal.getNavigationSiteMap(self.req, only_folders=True))
        self.assertEqual(len(res), 1)
        self.assertEqual(t(res[0]), 'info/sub_approved')

    def test_json_with_subportals(self):
        t = self.t
        manage_addNySite(self.portal.info, id='subsite', title='subsite',
                         lang='en')

        self.req.form = {'node': 'info'}
        res = json.loads(self.portal.getNavigationSiteMap(self.req, subportals=True))
        self.assertEqual(len(res), 5)

        self.assertEqual(t(res[0]), 'info/accessibility')
        self.assertEqual(t(res[1]), 'info/cookie_policy')
        self.assertEqual(t(res[2]), 'info/contact')
        self.assertEqual(t(res[3]), 'info/sub_approved')
        self.assertEqual(t(res[4]), 'info/subsite')
        self.assertEqual(len(res[4]['children']), 1)
        self.assertEqual(t(res[4]['children'][0]), 'info/subsite/info')
        self.assertEqual(t(res[4]['children'][0]['children'][0]),
                         'info/subsite/info/accessibility')
        self.assertEqual(len(res[4]['children'][0]['children']), 3)

        self.req.form = {'node': 'info/subsite'}
        res = json.loads(self.portal.getNavigationSiteMap(self.req,
                                                          only_folders=True,
                                                          subportals=True))
        self.assertEqual(len(res), 1)
        self.assertEqual(t(res[0]), 'info/subsite/info')

class NonPortalRelatedTestCase(unittest.TestCase):

    def test_process_querystring(self):
        site = NySite('test')
        arg_expected = [
            ('', ''),
            ('x', ''),
            ('x=oops', 'x=oops'),
            ('x=oops&skey=&rkey=23', 'x=oops'),
            ('x=&skey=&rkey=23', ''),
            ('start=zz&skey=34&rkey=23&m=&n=oops', 'n=oops'),
            ('m=once&f&start=zz&rkey=1&x=again&n=oops', 'm=once&x=again&n=oops')
        ]
        for arg, expected in arg_expected:
            self.assertEqual(site.process_querystring(arg), expected)
