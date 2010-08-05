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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AuthenticationUnitTest))
    return suite
