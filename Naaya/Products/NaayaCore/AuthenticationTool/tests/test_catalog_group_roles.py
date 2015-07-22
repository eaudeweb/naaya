from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.AuthenticationTool.plugins.plugLDAPUserFolder import plugLDAPUserFolder


class GroupRolesCatalogTest(NaayaTestCase):
    """ test catalogging group local roles """

    def setUp(self):
        super(GroupRolesCatalogTest, self).setUp()
        acl_path = self.portal.aq_parent.acl_users.absolute_url(1)
        self.auth_tool = self.portal.getAuthenticationTool()
        self.auth_tool.manageAddSource(acl_path, 'Eionet')
        source = self.auth_tool.getSources()[0]
        self.source_id = source.getId()
        cat_tool = self.portal.getCatalogTool()
        self.info_folder = self.portal.info
        self.satellite = self.portal.acl_satellite.__of__(self.info_folder)
        self.source = self.auth_tool.getSources()[0]
        self.source.__class__ = plugLDAPUserFolder

    def tearDown(self):
        self.auth_tool.manageDeleteSource(self.id)

    def _validate_role(self):
        mappings = self.source.get_groups_roles_map()
        self.assertEqual(len(mappings), 1)
        self.assertEqual(len(mappings['eea']), 1)
        role, location = mappings['eea'][0]
        self.assertEqual(role, 'Viewer')
        self.assertEqual(location['ob'], self.info_folder)

    def test_catalog_awareness(self):
        """ brain is updated on adding/rmving local roles for groups """
        cat_tool = self.portal.getCatalogTool()
        cat_tool.addColumn('ny_ldap_group_roles')
        self.satellite.add_group_roles('eea', ['Viewer'])
        brain = cat_tool({'path': self.info_folder.absolute_url(1),
                          'title': 'Information'})[0]
        self.assertTrue(brain.has_key('ny_ldap_group_roles'))
        self.assertEqual(brain.ny_ldap_group_roles, {'eea': ['Viewer']})
        self.satellite.remove_group_roles('eea', ['Viewer'])
        self.assertTrue(brain.has_key('ny_ldap_group_roles'))
        self.assertEqual(brain.ny_ldap_group_roles, {})
        cat_tool.delColumn('ny_ldap_group_roles')

    def test_works_with_catalog_support(self):
        """ group role assignment works without catalog setup (support) """
        cat_tool = self.portal.getCatalogTool()
        cat_tool.addColumn('ny_ldap_group_roles')
        self.satellite.add_group_roles('eea', ['Viewer'])
        self._validate_role()

    def test_works_without_catalog_support(self):
        """ group role assignment works without catalog setup (support) """
        self.satellite.add_group_roles('eea', ['Viewer'])
        self._validate_role()

    def test_works_with_missing_value(self):
        """ getting group role works with uncatalogged brain """
        # first update property, then add column in catalog
        self.satellite.add_group_roles('eea', ['Viewer'])
        cat_tool = self.portal.getCatalogTool()
        cat_tool.addColumn('ny_ldap_group_roles')
        self._validate_role()
