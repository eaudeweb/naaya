# python imports
from unittest import TestSuite, makeSuite
from copy import deepcopy

# Zope imports
from OFS.Folder import Folder
import transaction

# Naaya imports
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import check_username
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

# test imports
import ldap_config


class AuthenticationUnitTest(NaayaTestCase):
    """ unit tests for AuthenticationTool """

    def test_check_username(self):
        self.assertNotEquals(check_username('user1'), None)
        self.assertNotEquals(check_username('Us3r2'), None)
        self.assertNotEquals(check_username('USER3'), None)
        self.assertNotEquals(check_username('1337'), None)
        self.assertEquals(check_username('USER~'), None)
        self.assertEquals(check_username('!user'), None)
        self.assertEquals(check_username('&*%^@$'), None)

class LDAPBaseUnitTest(NaayaFunctionalTestCase):

    def afterSetUp(self):
        # check if ldap feature is available
        from nose.plugins.skip import SkipTest
        try:
            import dataflake.ldapconnection
            import Products.LDAPUserFolder
            import Products.LDAPUserFolder
        except ImportError, e:
            raise SkipTest, e

        from dataflake.ldapconnection.tests import fakeldap
        from Products.LDAPUserFolder import LDAPDelegate
        LDAPDelegate.c_factory = fakeldap.ldapobject.ReconnectLDAPObject
        fakeldap.clearTree()
        self.app.manage_delObjects(['acl_users'])
        self._add_ldap_user_folder()

        dg = ldap_config.defaults.get
        fakeldap.addTreeItems(dg('users_base'))
        fakeldap.addTreeItems(dg('groups_base'))

        self._add_ldap_schema()

        self._add_user(ldap_config.manager_user)
        self._add_user(ldap_config.user)
        self._add_user(ldap_config.user2)

        self.portal.acl_users.manageAddSource('acl_users', 'LDAP')
        transaction.commit()

    def _add_ldap_user_folder(self):
        from Products.LDAPUserFolder import manage_addLDAPUserFolder
        dg = ldap_config.defaults.get
        manage_addLDAPUserFolder(self.app)
        luf = self.app.acl_users
        host, port = dg('server').split(':')
        luf.manage_addServer(host, port=port)
        luf.manage_edit(dg('title'),
                        dg('login_attr'),
                        dg('uid_attr'),
                        dg('users_base'),
                        dg('users_scope'),
                        dg('roles'),
                        dg('groups_base'),
                        dg('groups_scope'),
                        dg('binduid'),
                        dg('bindpwd'),
                        binduid_usage = dg('binduid_usage'),
                        rdn_attr = dg('rdn_attr'),
                        local_groups = dg('local_groups'),
                        implicit_mapping = dg('implicit_mapping'),
                        encryption = dg('encryption'),
                        read_only = dg('read_only'))

    def _add_ldap_schema(self):
        schema = ldap_config.schema
        luf = self.app.acl_users
        for item in schema.values():
            luf.manage_addLDAPSchemaItem(**item)

    def _add_user(self, user_dict):
        def get_group_names():
            return [group[0] for group in self.app.acl_users.getGroups()]

        for role in user_dict['user_roles']:
            if role not in get_group_names():
                self.app.acl_users.manage_addGroup(role)
                self.app.acl_users.manage_addGroupMapping(role, role)
        for group in user_dict['ldap_groups']:
            if group not in get_group_names():
                self.app.acl_users.manage_addGroup(group)
        self.app.acl_users.manage_addUser(REQUEST=None, kwargs=user_dict)

class LDAPUnitTest(LDAPBaseUnitTest):
    def test_luf_instantiation(self):
        dg = ldap_config.defaults.get
        acl = self.app.acl_users
        ae = self.assertEqual
        ae(self.app.__allow_groups__, acl)
        ae(acl.getProperty('title'), dg('title'))
        ae(acl.getProperty('_login_attr'), dg('login_attr'))
        ae(acl.getProperty('_uid_attr'), dg('uid_attr'))
        ae(acl.getProperty('users_base'), dg('users_base'))
        ae(acl.getProperty('users_scope'), dg('users_scope'))
        ae(acl.getProperty('_roles'), [dg('roles')])
        ae(acl.getProperty('groups_base'), dg('groups_base'))
        ae(acl.getProperty('groups_scope'), dg('groups_scope'))
        ae(acl.getProperty('_binduid'), dg('binduid'))
        ae(acl.getProperty('_bindpwd'), dg('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), dg('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), dg('rdn_attr'))
        ae(acl.getProperty('_local_groups'), not not dg('local_groups'))
        ae(acl.getProperty('_implicit_mapping'), not not dg('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), dg('encryption'))
        ae(acl.getProperty('_extra_user_filter'), dg('extra_user_filter'))
        ae(acl.getProperty('read_only'), not not dg('read_only'))
        ae(len(acl._cache('anonymous').getCache()), 0)
        ae(len(acl._cache('authenticated').getCache()), 0)
        ae(len(acl._cache('negative').getCache()), 0)
        ae(len(acl.getSchemaConfig().keys()), len(ldap_config.schema))
        ae(len(acl.getSchemaDict()), len(ldap_config.schema))
        ae(len(acl._groups_store), 0)
        ae(len(acl.getProperty('additional_groups')), 0)
        ae(len(acl.getGroupMappings()), 2)
        ae(len(acl.getServers()), 1)

        ug = ldap_config.user.get
        self.browser_do_login(ug('uid'), ug('user_pw'))
        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AuthenticationUnitTest))
    suite.addTest(makeSuite(LDAPUnitTest))
    return suite
