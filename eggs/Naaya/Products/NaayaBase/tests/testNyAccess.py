from BeautifulSoup import BeautifulSoup

import transaction
from AccessControl import getSecurityManager
from AccessControl.Permission import Permission

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.NyAccess import NyAccess
from Products.Naaya.NySite import NySite

class NyAccessTestCase(NaayaFunctionalTestCase):
    def setUp(self):
        super(NyAccessTestCase, self).setUp()

        addNyFolder(self.portal.info,
                    'testfolder',
                    contributor='admin',
                    submission=1)
        self.testfolder = self.portal.info.testfolder

        # NOTE: this is *not* the way to use NyAccess. It should never
        # be stored in the database. It should be set as an attribute
        # to a *class*, like NyForum.
        self.testfolder._setOb('ny_access',
                NyAccess('ny_access',
                         {'View': 'View', 'View History': 'View History'}))

        transaction.commit()

    def test_structure(self):
        self.assertTrue(self.testfolder.ny_access.getObject() is self.testfolder)

    def test_roles(self):
        set_mapping = {'View': ('Manager',), 'View History': ('Manager', 'Reviewer')}

        # internal test: all the permissions get new values
        self.assertEqual(set(set_mapping.keys()), 
                         set(self.testfolder.ny_access.permissions))

        self.testfolder.ny_access.setPermissionMapping(set_mapping)

        got_mapping = self.testfolder.ny_access.getPermissionMapping()

        self.assertEqual(set_mapping, got_mapping)

    def _test_user_perm(self, username, password, permname, value):
        self.browser_do_login(username, password)
        logged_user = getSecurityManager().getUser()
        self.assertEqual(logged_user.getUserName(), username)

        # this is changed to match the _check_context
        # it is based on the structure of the site&zope_app
        # this has to change if the acl_users change
        if isinstance(logged_user.aq_parent.aq_parent, NySite):
            context_object = logged_user.aq_parent.aq_parent.info.testfolder
        else:
            context_object = logged_user.aq_parent.aq_parent.portal.info.testfolder

        self.assertEqual(logged_user._check_context(context_object), 1)

        if value is None:
            self.assertTrue(context_object.checkPermission(permname) is None)
        else:
            self.assertEqual(context_object.checkPermission(permname), value)

        self.browser_do_logout()

    def test_users(self):
        set_mapping = {'View': ('Contributor',), 
                       'View History': ('Contributor', 'Reviewer')}
        self.testfolder.ny_access.setPermissionMapping(set_mapping)
        transaction.commit()

        self._test_user_perm('contributor', 'contributor', 'View', 1)
        self._test_user_perm('reviewer', 'reviewer', 'View', None)

        self._test_user_perm('contributor', 'contributor', 'View History', 1)
        self._test_user_perm('reviewer', 'reviewer', 'View History', 1)

    def test_users_functional(self):
        set_mapping = {'View': ('Contributor',),
                       'View History': ('Contributor', 'Reviewer')}
        self.testfolder.ny_access.setPermissionMapping(set_mapping)
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go(self.testfolder.absolute_url(1) +
                        '/manage_permissionForm?permission_to_manage=View')
        form = self.browser.get_form(1)
        field = self.browser.get_form_field(form, 'roles:list')
        for item in field.items:
            if item.name == 'Contributor':
                self.assertTrue(item._selected)
            else:
                self.assertFalse(item._selected)

        self.browser.go(self.testfolder.absolute_url(1) + 
                        '/manage_permissionForm?permission_to_manage=View%20History')
        form = self.browser.get_form(1)
        field = self.browser.get_form_field(form, 'roles:list')
        for item in field.items:
            if item.name == 'Contributor' or item.name == 'Reviewer':
                self.assertTrue(item._selected)
            else:
                self.assertFalse(item._selected)

        self.browser_do_logout()

    def test_get_permissions(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.testfolder.absolute_url(1) +
                        '/manage_permissionForm?permission_to_manage=View')
        form = self.browser.get_form(1)
        form['roles:list'] = ('Contributor',)
        self.browser.submit()

        self.assertEqual(self.testfolder.ny_access.getPermissionMapping()['View'],
                         ['Contributor'])

        self.browser_do_logout()

class NyAccess2LevelTestCase(NaayaFunctionalTestCase):
    def setUp(self):
        super(NyAccess2LevelTestCase, self).setUp()

        self.perm1, self.perm2 = 'View', 'View History'
        self.role1, self.role2 = 'Contributor', 'Reviewer'

        addNyFolder(self.portal.info,
                    'testfolderparent',
                    contributor='admin',
                    submission=1)
        self.testfolderparent = self.portal.info.testfolderparent

        addNyFolder(self.testfolderparent,
                    'testfolder',
                    contributor='admin',
                    submission=1)
        self.testfolder = self.testfolderparent.testfolder

        # NOTE: this is *not* the way to use NyAccess. It should never
        # be stored in the database. It should be set as an attribute
        # to a *class*, like NyForum.
        self.testfolderparent._setOb('ny_access',
                NyAccess('ny_access',
                         {self.perm1: self.perm1, self.perm2: self.perm2}))

        self.testfolder._setOb('ny_access',
                NyAccess('ny_access',
                         {self.perm1: self.perm1, self.perm2: self.perm2}))

        # default permission map
        # parent folder does not inherit permissions
        permission = Permission(self.perm1, (), self.testfolderparent)
        permission.setRoles((self.role1, 'Manager'))
        permission = Permission(self.perm2, (), self.testfolderparent)
        permission.setRoles((self.role2, 'Manager'))
        # child folder permissions
        permission = Permission(self.perm1, (), self.testfolder)
        permission.setRoles([self.role2])
        permission = Permission(self.perm2, (), self.testfolder)
        permission.setRoles((self.role1, 'Manager'))

        transaction.commit()

    def _acquired(self, soup, role, perm):
        star_id = 'acquired' + role + perm
        return soup.find('img', attrs={'id': star_id}) is not None

    def test_viewPermissions(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.testfolder.absolute_url(1) + '/ny_access')
        soup = BeautifulSoup(self.browser.get_html())
        form = self.browser.get_form('save-permissions')

        # perm1 test
        field_name = 'acquires' + self.perm1
        field = self.browser.get_form_field(form, field_name)
        self.assertEqual(len(field.items), 1)
        self.assertTrue(field.items[0]._selected)

        field_name = self.perm1 + ':list'
        field = self.browser.get_form_field(form, field_name)
        self.assertEqual(len(field.items), len(self.testfolder.validRoles()) - 2)
        items_by_name = dict((item.name, item) for item in field.items)
        self.assertTrue(self.role1 in items_by_name.keys())
        self.assertTrue(self.role2 in items_by_name.keys())

        self.assertFalse(items_by_name[self.role1]._selected)
        self.assertTrue(self._acquired(soup, self.role1, self.perm1))
        self.assertTrue(items_by_name[self.role2]._selected)
        self.assertFalse(self._acquired(soup, self.role2, self.perm1))

        # perm2 test
        field_name = 'acquires' + self.perm2
        field = self.browser.get_form_field(form, field_name)
        self.assertEqual(len(field.items), 1)
        self.assertFalse(field.items[0]._selected)

        field_name = self.perm2 + ':list'
        field = self.browser.get_form_field(form, field_name)
        self.assertEqual(len(field.items), len(self.testfolder.validRoles()) - 2)
        items_by_name = dict((item.name, item) for item in field.items)
        self.assertTrue(self.role1 in items_by_name.keys())
        self.assertTrue(self.role2 in items_by_name.keys())

        self.assertTrue(items_by_name[self.role1]._selected)
        self.assertFalse(self._acquired(soup, self.role1, self.perm2))
        self.assertFalse(items_by_name[self.role2]._selected)
        self.assertFalse(self._acquired(soup, self.role2, self.perm2))

        self.browser_do_logout()

    def test_savePermissions(self):
        saved_mapping = self.testfolder.ny_access.getPermissionMapping()

        self.browser_do_login('admin', '')

        self.browser.go(self.testfolder.absolute_url(1) + '/ny_access')
        form = self.browser.get_form('save-permissions')

        form['acquires'+self.perm1] = []
        form[self.perm1+':list'] = [self.role1, self.role2]
        form['acquires'+self.perm2] = ['on']
        form[self.perm2+':list'] = [self.role2]
        self.browser.clicked(form, self.browser.get_form_field(form, 'known_roles:list'))
        self.browser.submit()

        form = self.browser.get_form('save-permissions')
        soup = BeautifulSoup(self.browser.get_html())

        # perm1 test
        field_name = 'acquires' + self.perm1
        field = self.browser.get_form_field(form, field_name)
        self.assertFalse(field.items[0]._selected)

        field_name = self.perm1 + ':list'
        field = self.browser.get_form_field(form, field_name)
        items_by_name = dict((item.name, item) for item in field.items)

        self.assertTrue(items_by_name[self.role1]._selected)
        self.assertFalse(self._acquired(soup, self.role1, self.perm1))
        self.assertTrue(items_by_name[self.role2]._selected)
        self.assertFalse(self._acquired(soup, self.role2, self.perm1))

        # perm2 test
        field_name = 'acquires' + self.perm2
        field = self.browser.get_form_field(form, field_name)
        self.assertTrue(field.items[0]._selected)

        field_name = self.perm2 + ':list'
        field = self.browser.get_form_field(form, field_name)
        items_by_name = dict((item.name, item) for item in field.items)

        self.assertFalse(items_by_name[self.role1]._selected)
        self.assertFalse(self._acquired(soup, self.role1, self.perm2))
        self.assertTrue(items_by_name[self.role2]._selected)
        self.assertTrue(self._acquired(soup, self.role2, self.perm2))

        # redo the changes
        form['acquires'+self.perm1] = ['on']
        form[self.perm1+':list'] = [self.role2]
        form['acquires'+self.perm2] = []
        form[self.perm2+':list'] = [self.role1]
        self.browser.clicked(form, self.browser.get_form_field(form, 'known_roles:list'))
        self.browser.submit()

        self.browser_do_logout()

        self.assertEqual(saved_mapping, self.testfolder.ny_access.getPermissionMapping())
