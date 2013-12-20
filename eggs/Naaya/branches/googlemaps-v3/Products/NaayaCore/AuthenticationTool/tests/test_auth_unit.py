from warnings import warn
from nose.plugins.skip import SkipTest
import transaction
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import check_username
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NySite import manage_addNySite
import ldap_config
import mock_ldap


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

    def test_getUsersRoles(self):
        acl_users = self.portal.acl_users
        acl_users._doAddUser('user1', 'user1', ['Contributor'], '',
                             'User name', 'User other name', 'user1@example.com')
        manage_addNySite(self.portal, id='subsite', title='subsite', lang='en')
        acl_users.manage_addUsersRoles('user1', roles=['Administrator'], location='info')
        acl_users.manage_addUsersRoles('user1', roles=['Manager'], location='subsite/info')
        users_roles = acl_users.getUsersRoles()
        self.assertTrue('user1' in users_roles)
        user1_roles = users_roles['user1']
        self.assertTrue((['Contributor'], '') in user1_roles)
        self.assertTrue((['Administrator'], 'info') in user1_roles)
        self.assertTrue((['Manager'], 'subsite/info') in user1_roles)

class LDAPBaseUnitTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        warn("LDAPBaseUnitTest is deprecated")
        if not mock_ldap.is_available:
            raise SkipTest

        mock_ldap.quick_setup(self.app, self.portal)
        transaction.commit()

    def _add_ldap_user_folder(self):
        warn("LDAPBaseUnitTest is deprecated")
        mock_ldap.add_ldap_user_folder(self.app)

    def _add_ldap_schema(self):
        warn("LDAPBaseUnitTest is deprecated")
        mock_ldap.add_ldap_schema(self.app)

    def _add_user(self, user_dict):
        warn("LDAPBaseUnitTest is deprecated")
        mock_ldap.add_user(self.app, user_dict)

class LDAPUnitTest(NaayaFunctionalTestCase):
    def setUp(self):
        super(LDAPUnitTest, self).setUp()
        if not mock_ldap.is_available:
            from nose.plugins.skip import SkipTest
            raise SkipTest

        mock_ldap.quick_setup(self.app, self.portal)
        transaction.commit()

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
