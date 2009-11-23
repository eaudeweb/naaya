from Testing.ZopeTestCase import TestCase
from unittest import TestSuite, makeSuite

from Products.NaayaCore.AuthenticationTool.AuthenticationTool import check_username


class AuthenticationUnitTest(TestCase):
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
