from unittest import SkipTest

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from . import mock_ldap


class LDAPGroupsIntegrationTest(NaayaTestCase):
    """ LDAP group membership and group roles against a fake LDAP server """

    def afterSetUp(self):
        if not mock_ldap.is_available:
            raise SkipTest('dataflake.fakeldap is not installed')
        mock_ldap.quick_setup(self.app, self.portal)
        transaction.commit()
        self.plugin = self.portal.acl_users.getSources()[0]
        self.ldap_folder = self.plugin.getUserFolder()

    def user(self, user_id):
        return self.app.acl_users.getUser(user_id)

    def test_group_member_ids(self):
        # 'Manager' is the bind user LDAPUserFolder adds to new groups
        self.assertEqual(sorted(self.plugin.group_member_ids('Group1')),
                         ['Manager', 'test', 'test2'])
        self.assertTrue(self.plugin.user_in_group(self.user('admin'),
                                                  'Group3'))
        self.assertFalse(self.plugin.user_in_group(self.user('admin'),
                                                   'Group1'))

    def test_group_role_from_membership(self):
        info = self.portal.info
        info.acl_satellite.add_group_roles('Group1', ['Contributor'])
        self.assertEqual(info.acl_satellite.getAdditionalRoles(
            self.user('test')), ['Contributor'])
        self.assertEqual(info.contact.acl_satellite.getAdditionalRoles(
            self.user('test')), ['Contributor'])
        self.assertEqual(info.acl_satellite.getAdditionalRoles(
            self.user('admin')), [])
        self.assertEqual(self.portal.acl_satellite.getAdditionalRoles(
            self.user('test')), [])

    def test_local_roles_by_groups(self):
        self.portal.info.acl_satellite.add_group_roles('Group1', ['Reviewer'])
        roles = self.plugin.get_local_roles_by_groups(self.user('test'))
        self.assertEqual(list(roles), ['Group1'])
        [(role, location)] = roles['Group1']
        self.assertEqual((role, location['path']), ('Reviewer', 'info'))
        self.assertEqual(
            self.plugin.get_local_roles_by_groups(self.user('admin')), {})

    def test_map_group_to_role(self):
        self.plugin.map_group_to_role('Group1', ['Contributor'], 'info')
        self.assertEqual(self.portal.info.__ny_ldap_group_roles__,
                         {'Group1': ['Contributor']})
        self.plugin.map_group_to_role('Group2', ['Reviewer'], '/')
        self.assertEqual(self.portal.__ny_ldap_group_roles__,
                         {'Group2': ['Reviewer']})
        self.assertFalse(hasattr(self.app.aq_base, '__ny_ldap_group_roles__'))
        self.assertRaises(ValueError, self.plugin.map_group_to_role,
                          'Group1', ['Contributor'], 'missing')
        self.plugin.revoke_group_role('Group1', 'Contributor', 'info')
        self.assertEqual(self.portal.info.__ny_ldap_group_roles__, {})

    def test_users_by_role(self):
        users = self.plugin.getUsersByRole(self.ldap_folder,
                                           [('Group1', 'cn=Group1')])
        self.assertEqual(sorted(u.user_id for u in users), ['test', 'test2'])
        self.assertEqual(self.plugin.getUsersByRole(self.ldap_folder), ())

    def test_find_users(self):
        self.portal.REQUEST.form['search_user'] = '1'
        self.portal.REQUEST.other['search_user'] = '1'
        users = self.plugin.findLDAPUsers(self.ldap_folder, params='uid',
                                          term='test2')
        self.assertEqual([u.user_id for u in users], ['test2'])
        self.assertEqual(self.plugin.findLDAPUsers(self.ldap_folder,
                                                   params='uid', term=''), ())
