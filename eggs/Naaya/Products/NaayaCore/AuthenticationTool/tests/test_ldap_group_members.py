import unittest
from unittest import mock

from Products.NaayaCore.AuthenticationTool.plugins.plugLDAPUserFolder import (
    plugLDAPUserFolder)

try:
    import ldap
except ImportError:
    ldap = None


@unittest.skipIf(ldap is None, 'python-ldap is not installed')
class GroupMembersTest(unittest.TestCase):

    def make_plugin(self, members):
        source = mock.Mock()
        source.absolute_url.return_value = 'acl_users'
        plugin = plugLDAPUserFolder('ldap', source, 'LDAP')
        self.delegate = mock.Mock()
        self.delegate.search.return_value = {
            'size': 1, 'results': [{'uniqueMember': members}]}
        plugin.getUserFolder = lambda: None
        plugin.getRootDN = lambda folder: 'ou=Roles,o=EIONET'
        plugin.getGroupScope = lambda folder: 2
        plugin.get_ldap_delegate = lambda: self.delegate
        plugin.get_source_user_info = lambda uid: mock.Mock(
            full_name='Name of %s' % uid)
        return plugin

    def test_group_member_ids(self):
        plugin = self.make_plugin(['uid=jdoe,ou=Users,o=EIONET', ''])
        self.assertEqual(plugin.group_member_ids('grp-ids(x)'), ['jdoe'])
        # the group id is escaped in the LDAP filter
        self.assertEqual(self.delegate.search.call_args[0][2],
                         r'(cn=grp-ids\28x\29)')

    def test_users_by_role_member_attribute(self):
        plugin = self.make_plugin([])
        plugin._get_users_base = lambda: 'ou=Users,o=EIONET'
        self.delegate.search.return_value = {'size': 1, 'results': [
            {'member': ['uid=jdoe,ou=Users,o=EIONET', 'cn=nested,ou=Roles']}]}
        users = plugin.getUsersByRole(None, [('grp(x)', 'cn=grp')])
        self.assertEqual([u.full_name for u in users], ['Name of jdoe'])
        self.assertEqual(self.delegate.search.call_args[0][2],
                         r'(cn=grp\28x\29)')

    def test_get_group_members(self):
        plugin = self.make_plugin(['uid=jdoe,ou=Users,o=EIONET',
                                   'uid=asmith,ou=Users,o=EIONET'])
        members = plugin.get_group_members('grp-members')
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0], {'user_id': 'jdoe',
                                      'user_name': 'Name of jdoe'})
