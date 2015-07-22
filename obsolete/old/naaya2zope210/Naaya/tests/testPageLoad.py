from NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        self.login()
        portal = self.app.portal
        portal.admin_addremotechannels_aggregator('Test')
        addNyFolder(portal.info, 'test')

    def beforeTearDown(self):
        portal = self.app.portal
        portal.info.manage_delObjects('test')
        ca = portal.getSyndicationTool().objectIds(['Naaya Channel Aggregator'])
        portal.admin_deleteremotechannels_aggregator(ids=ca)

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        portal = self.app.portal

        portal.index_html()
        portal.messages_html()
        portal.messages_box()
        portal.languages_box()
        portal.login_html()
        portal.logout_html()
        portal.unauthorized_html()
        portal.search_html()
        portal.external_search_html()
        portal.sitemap_html()
        portal.sitemap_add_html()
        portal.feedback_html()
        portal.requestrole_html()
        portal.profile_html()
        portal.localchannels_rdf()

        portal.admin_centre_html()
        portal.admin_metadata_html()
        portal.admin_email_html()
        portal.admin_logos_html()
        portal.admin_properties_html()
        portal.admin_layout_html()
        portal.admin_documentation_html()
        portal.admin_users_html()
        portal.admin_adduser_html()
        portal.admin_addrole_html()
        portal.admin_roles_html()
        portal.admin_sources_html()
        portal.admin_translations_html()
        portal.admin_messages_html()
        portal.admin_importexport_html()
        portal.admin_linkslists_html()
        portal.admin_linkslist_html()
        portal.admin_reflists_html()
        portal.admin_reflist_html()
        portal.admin_network_html()
        portal.admin_basket_html()
        portal.admin_validation_html()
        portal.admin_validation_tree_html()
        portal.admin_versioncontrol_html()
        portal.admin_maintopics_html()
        portal.admin_localchannels_html()
        portal.admin_remotechannels_html()
        portal.admin_remotechannels_aggregators_html()
        portal.admin_leftportlets_html()
        portal.admin_frontportlets_html()
        portal.admin_rightportlets_html()
        portal.admin_specialportlets_html()
        portal.admin_remotechportlets_html()
        portal.admin_localchportlets_html()
        portal.admin_folderportlets_html()
        portal.admin_linksportlets_html()
        portal.admin_htmlportlets_html()
        portal.admin_delmesg_html()

        id_channel = portal.getSyndicationTool().objectIds([
            'Naaya Channel Aggregator'])[0]

        portal.channel_details_html(request={'id_channel': id_channel})
        portal.admin_edituser_html(request={'name': 'contributor'})

    def test_folder_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        folder = self.app.portal.info

        folder.index_atom(REQUEST={})
        folder.index_rdf(REQUEST={})
        folder.index_html()
        folder.folder_add_html()
        folder.feedback_html()
        folder.comments_rdf()
        folder.restrict_html()
        folder.sortorder_html()
        folder.basketofvalidation_html()
        folder.basketofapprovals_html()
        folder.editlogo_html()
        folder.edit_html()
        folder.subobjects_html()

        folder.administration_feedback_html()
        folder.administration_portlets_html()
        folder.administration_source_html()
        folder.administration_users_html()
        folder.administration_logo_html()
        folder.administration_basket_html()

        ids = folder.objectIds()
        folder.renameobject_html(request={'id': ids})

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
