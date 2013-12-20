import transaction
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class RoleTest(NaayaTestCase):
    """ test admin role pages """


    def test_delete_user(self):
        acl_users = self.portal.acl_users
        acl_users._doAddUser('user1', 'user1', ['Contributor'], '',
                             'User name', 'User other name', 'user1@example.com')
        acl_users.manage_addUsersRoles('user1', roles=['Administrator'], location='info')
        assert self.portal.info.__ac_local_roles__['user1'] == ['Administrator']
        acl_users.manage_delUsers('user1')
        assert 'user1' not in acl_users.getUserNames()
        assert not self.portal.info.__ac_local_roles__.has_key('user1')
