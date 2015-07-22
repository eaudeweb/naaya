import base64
from webob import Request
import transaction

from NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder

class PageLoadTests(NaayaFunctionalTestCase):
    def afterSetUp(self):
        self.login()
        portal = self.app.portal
        portal.admin_addremotechannels_aggregator('Test')
        addNyFolder(portal.info, 'test')
        transaction.commit()

    def beforeTearDown(self):
        portal = self.app.portal
        portal.info.manage_delObjects('test')
        ca = portal.getSyndicationTool().objectIds(['Naaya Channel Aggregator'])
        portal.admin_deleteremotechannels_aggregator(ids=ca)
        transaction.commit()

    def assert_page_ok(self, url, user_id=None):
        request = Request.blank(url)
        if user_id is not None:
            if user_id != 'admin':
                raise ValueError("I only know about the admin account, "
                                 "who is %r?" % user_id)
            request.authorization = 'Basic %s' % base64.b64encode('admin:')
        response = request.get_response(self.wsgi_request)
        assert response.status == '200 OK', repr(response)

    def test_page_load(self):
        self.assert_page_ok('/portal/')
        self.assert_page_ok('/portal/messages_html')
        self.assert_page_ok('/portal/messages_box')
        self.assert_page_ok('/portal/languages_box')
        self.assert_page_ok('/portal/login_html')
        self.assert_page_ok('/portal/logout_html')
        self.assert_page_ok('/portal/unauthorized_html')
        self.assert_page_ok('/portal/search_html')
        self.assert_page_ok('/portal/external_search_html')
        self.assert_page_ok('/portal/sitemap_html')
        self.assert_page_ok('/portal/sitemap_add_html')
        self.assert_page_ok('/portal/feedback_html')
        self.assert_page_ok('/portal/requestrole_html')
        self.assert_page_ok('/portal/localchannels_rdf')

        self.assert_page_ok('/portal/admin_centre_html', 'admin')
        self.assert_page_ok('/portal/admin_metadata_html', 'admin')
        self.assert_page_ok('/portal/admin_email_html', 'admin')
        self.assert_page_ok('/portal/admin_logos_html', 'admin')
        self.assert_page_ok('/portal/admin_properties_html', 'admin')
        self.assert_page_ok('/portal/admin_layout_html', 'admin')
        self.assert_page_ok('/portal/admin_documentation_html', 'admin')
        self.assert_page_ok('/portal/admin_users_html', 'admin')
        self.assert_page_ok('/portal/admin_adduser_html', 'admin')
        self.assert_page_ok('/portal/admin_roles_html', 'admin')
        self.assert_page_ok('/portal/admin_sources_html', 'admin')
        self.assert_page_ok('/portal/admin_linkslists_html', 'admin')
        self.assert_page_ok('/portal/admin_linkslist_html', 'admin')
        self.assert_page_ok('/portal/admin_reflists_html', 'admin')
        self.assert_page_ok('/portal/admin_reflist_html', 'admin')
        self.assert_page_ok('/portal/admin_network_html', 'admin')
        self.assert_page_ok('/portal/admin_basket_html', 'admin')
        self.assert_page_ok('/portal/admin_validation_html', 'admin')
        self.assert_page_ok('/portal/admin_validation_tree_html', 'admin')
        self.assert_page_ok('/portal/admin_versioncontrol_html', 'admin')
        self.assert_page_ok('/portal/admin_maintopics_html', 'admin')
        self.assert_page_ok('/portal/admin_localchannels_html', 'admin')
        self.assert_page_ok('/portal/admin_remotechannels_html', 'admin')
        self.assert_page_ok('/portal/admin_remotechannels_aggregators_html',
                            'admin')
        self.assert_page_ok('/portal/admin_specialportlets_html', 'admin')
        self.assert_page_ok('/portal/admin_remotechportlets_html', 'admin')
        self.assert_page_ok('/portal/admin_localchportlets_html', 'admin')
        self.assert_page_ok('/portal/admin_folderportlets_html', 'admin')
        self.assert_page_ok('/portal/admin_linksportlets_html', 'admin')
        self.assert_page_ok('/portal/admin_htmlportlets_html', 'admin')

        id_channel = self.portal.getSyndicationTool().objectIds([
            'Naaya Channel Aggregator'])[0]

        self.assert_page_ok('/portal/channel_details_html?id_channel=%s' %
                            id_channel)
        self.assert_page_ok('/portal/admin_edituser_html?name=contributor',
                            'admin')

    def test_folder_page_load(self):
        """ Try to render some basic pages """

        self.assert_page_ok('/portal/info/index_atom')
        self.assert_page_ok('/portal/info/index_rdf')
        self.assert_page_ok('/portal/info/index_html')
        self.assert_page_ok('/portal/info/folder_add_html', 'admin')
        self.assert_page_ok('/portal/info/feedback_html')
        self.assert_page_ok('/portal/info/comments_rdf')
        self.assert_page_ok('/portal/info/restrict_html', 'admin')
        self.assert_page_ok('/portal/info/sortorder_html', 'admin')
        self.assert_page_ok('/portal/info/basketofvalidation_html', 'admin')
        self.assert_page_ok('/portal/info/basketofapprovals_html', 'admin')
        self.assert_page_ok('/portal/info/editlogo_html', 'admin')
        self.assert_page_ok('/portal/info/edit_html', 'admin')
        self.assert_page_ok('/portal/info/subobjects_html', 'admin')

        self.assert_page_ok('/portal/info/administration_feedback_html',
                            'admin')
        self.assert_page_ok('/portal/info/administration_portlets_html',
                            'admin')
        self.assert_page_ok('/portal/info/administration_source_html', 'admin')
        self.assert_page_ok('/portal/info/administration_users_html', 'admin')
        self.assert_page_ok('/portal/info/administration_logo_html', 'admin')
        self.assert_page_ok('/portal/info/administration_basket_html', 'admin')
