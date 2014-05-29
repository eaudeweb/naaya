"""
Mock LDAP server and helper functions.

Use like this::

    from nose.plugins.skip import SkipTest
    from Products.NaayaCore.AuthenticationTool.tests import mock_ldap
    from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
    import transaction

    class MyTest(NaayaTestCase):
        def setUp(self):
            super(MyTest, self).setUp()
            if not mock_ldap.is_available:
                raise SkipTest
            mock_ldap.quick_setup(self.app, self.portal)
            transaction.commit()

        def my_test(self):
            assert True # your test is probably more interesting

Alternatively you may want to call the lower-level API functions direcly:
`mock_ldap.setup_fakeldap`, `mock_ldap.add_ldap_schema`, `mock_ldap.add_user`.
"""

try:
    import dataflake.ldapconnection
    import Products.LDAPUserFolder
    import Products.LDAPUserFolder # import twice? why?
except ImportError, e:
    is_available = False
else:
    is_available = True

import ldap_config

def add_ldap_user_folder(app):
    from Products.LDAPUserFolder import manage_addLDAPUserFolder

    dg = ldap_config.defaults.get
    manage_addLDAPUserFolder(app)
    luf = app.acl_users
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
    luf.manage_deleteLDAPSchemaItems(luf._ldapschema.keys()) # clear the schema

def setup_fakeldap(app):
    from dataflake.ldapconnection.tests import fakeldap
    from Products.LDAPUserFolder import LDAPDelegate

    LDAPDelegate.c_factory = fakeldap.ldapobject.ReconnectLDAPObject
    fakeldap.clearTree()
    app.manage_delObjects(['acl_users'])
    add_ldap_user_folder(app)

    dg = ldap_config.defaults.get
    fakeldap.addTreeItems(dg('users_base'))
    fakeldap.addTreeItems(dg('groups_base'))

def add_ldap_schema(app):
    schema = ldap_config.schema
    luf = app.acl_users
    for item in schema.values():
        luf.manage_addLDAPSchemaItem(**item)

def add_user(app, user_dict):
    def get_group_names():
        return [group[0] for group in app.acl_users.getGroups()]

    for role in user_dict.get('user_roles', []):
        if role not in get_group_names():
            app.acl_users.manage_addGroup(role)
            app.acl_users.manage_addGroupMapping(role, role)
    for group in user_dict.get('ldap_groups', []):
        if group not in get_group_names():
            app.acl_users.manage_addGroup(group)
    app.acl_users.manage_addUser(REQUEST=None, kwargs=user_dict)

def quick_setup(app, portal, add_users=True):
    setup_fakeldap(app)
    add_ldap_schema(app)
    if add_users:
        add_user(app, ldap_config.manager_user)
        add_user(app, ldap_config.user)
        add_user(app, ldap_config.user2)
    portal.acl_users.manageAddSource('acl_users', 'LDAP')
