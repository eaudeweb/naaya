from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests import utils as test_utils
from Products.NaayaCore.AuthenticationTool.plugins import plugLDAPUserFolder

def set_group_role(obj, group, role):
    if not hasattr(obj, '__ny_ldap_group_roles__'):
        obj.__ny_ldap_group_roles__ = {}
    obj.__ny_ldap_group_roles__.setdefault(group, []).append(role)

class MockUser(object):
    def __init__(self, groups):
        self.groups = groups

def mock_user_in_group_factory(self, user):
    return lambda group: group in user.groups

class LdapGroupRolesTest(NaayaTestCase):
    def afterSetUp(self):
        def add_folder(parent, name):
            addNyFolder(parent, name, contributor='contributor', submitted=1)
        add_folder(self.portal, 'fol1')
        add_folder(self.portal.fol1, 'kid')
        add_folder(self.portal.fol1, 'kid2')
        add_folder(self.portal.fol1.kid, 'grandkid')
        test_utils.replace(plugLDAPUserFolder.LdapSatelliteProvider,
                           'user_in_group_factory',
                           mock_user_in_group_factory)

    def beforeTearDown(self):
        test_utils.restore_all()
        self.portal.manage_delObjects(['fol1'])

    def assert_roles(self, obj, groups, roles):
        user = MockUser(groups)
        group_roles = obj.acl_satellite.getAdditionalRoles(user)
        self.assertEqual(set(group_roles), set(roles))

    def test_get_role(self):
        set_group_role(self.portal.fol1, 'group1', 'Contributor')
        self.assert_roles(self.portal.fol1, ['group1'], ['Contributor'])
        self.assert_roles(self.portal.fol1, ['group2'], [])

    def test_get_inherited_role(self):
        fol1 = self.portal.fol1
        kid = fol1.kid
        grandkid = kid.grandkid

        set_group_role(kid, 'group1', 'Contributor')

        self.assert_roles(fol1, ['group1'], [])
        self.assert_roles(kid, ['group1'], ['Contributor'])
        self.assert_roles(grandkid, ['group1'], ['Contributor'])

        self.assert_roles(fol1, ['group2'], [])
        self.assert_roles(kid, ['group2'], [])
        self.assert_roles(grandkid, ['group2'], [])

    def test_compose_roles(self):
        fol1 = self.portal.fol1
        kid = fol1.kid
        grandkid = kid.grandkid

        set_group_role(fol1, 'group1', 'A')
        set_group_role(kid, 'group1', 'B')
        set_group_role(kid, 'group2', 'C')
        set_group_role(grandkid, 'group2', 'D')

        self.assert_roles(fol1, ['group1', 'group2'], ['A'])
        self.assert_roles(kid, ['group1', 'group2'], ['A', 'B', 'C'])
        self.assert_roles(grandkid, ['group1', 'group2'], ['A', 'B', 'C', 'D'])

    def test_acquisition_escalation(self):
        fol1 = self.portal.fol1
        kid = fol1.kid
        kid2 = fol1.kid2

        set_group_role(fol1, 'group1', 'A')
        set_group_role(kid, 'group1', 'B')

        # kid2 is accessed in the context of kid
        kid2_in_kid = kid.kid2
        self.assert_roles(kid2_in_kid, ['group1'], ['A'])

    def test_add_roles(self):
        fol1 = self.portal.fol1
        add = fol1.acl_satellite.add_group_roles

        # string argument should not be allowed
        self.assertRaises(AssertionError, add, 'group1', 'A')

        add('group1', ['A', 'B'])
        self.assertEqual(fol1.__ny_ldap_group_roles__, {'group1': ['A', 'B']})

        fol1.acl_satellite.add_group_roles('group1', ['B', 'C'])
        self.assertEqual(fol1.__ny_ldap_group_roles__,
                         {'group1': ['A', 'B', 'C']})

        remove = fol1.acl_satellite.remove_group_roles
        # string argument should not be allowed
        self.assertRaises(AssertionError, remove, 'group1', 'A')

        self.assertRaises(ValueError, remove, 'group1', ['X'])

        fol1.acl_satellite.remove_group_roles('group1', ['A', 'C'])
        self.assertEqual(fol1.__ny_ldap_group_roles__, {'group1': ['B']})

        fol1.acl_satellite.remove_group_roles('group1', ['B'])
        self.assertEqual(fol1.__ny_ldap_group_roles__, {})
