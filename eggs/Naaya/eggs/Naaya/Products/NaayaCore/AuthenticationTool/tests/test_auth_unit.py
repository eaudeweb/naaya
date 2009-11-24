from unittest import TestSuite, makeSuite
from copy import deepcopy

from Products.NaayaCore.AuthenticationTool.AuthenticationTool import check_username
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase


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

    def test_add_perm_to_group(self):
        acl = self.portal.getAuthenticationTool()
        perm = deepcopy(acl.getPermission('Add content'))
        self.assertTrue('Naaya - Add Naaya Document objects' in perm['permissions'])

        # remove permission
        acl.manage_group_permission('Add content', 'Naaya - Add Naaya Document objects', 'remove')
        new_perm = acl.getPermission('Add content')
        self.assertFalse('Naaya - Add Naaya Document objects' in new_perm['permissions'])
        self.assertEqual(new_perm['description'], perm['description'])
        self.assertNotEqual(set(new_perm['permissions']), set(perm['permissions']))
        self.assertEqual(len(new_perm['permissions']), len(perm['permissions']) - 1)

        # add permission
        acl.manage_group_permission('Add content', 'Naaya - Add Naaya Document objects', 'add')
        new_perm = acl.getPermission('Add content')
        self.assertTrue('Naaya - Add Naaya Document objects' in new_perm['permissions'])
        self.assertEqual(new_perm['description'], perm['description'])
        self.assertEqual(set(new_perm['permissions']), set(perm['permissions']))
        self.assertEqual(len(new_perm['permissions']), len(perm['permissions']))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AuthenticationUnitTest))
    return suite
