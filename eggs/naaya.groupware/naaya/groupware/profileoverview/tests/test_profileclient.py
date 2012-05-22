import unittest
from mock import Mock

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.groupware.groupware_site import manage_addGroupwareSite, GroupwareSite

import naaya.groupware.profileoverview.profile
naaya.groupware.profileoverview.profile.usersdb = Mock()

from naaya.groupware.profileoverview.profile import ProfileClient


def common_setup(zope_app):
    zope_app.acl_users._delegate = Mock()
    zope_app.acl_users._delegate._servers = [{'host': '', 'port': ''}]
    zope_app.acl_users._doAddUser('nick', 'nick', [], '')

class InterestGroupsTestCase(NaayaTestCase):

    def setUp(self):
        super(InterestGroupsTestCase, self).setUp()
        common_setup(self.app)
        manage_addGroupwareSite(self.app, 'ig1', 'ig1')
        manage_addGroupwareSite(self.app, 'ig2', 'ig2')
        manage_addGroupwareSite(self.app, 'ig3', 'ig3')

    def test_igaccess(self):
        client = ProfileClient(self.app, self.app.acl_users.getUser('nick'))
        ac = client.access_in_igs()
        self.assertEqual(set(ac.keys()), set(['viewer']))
        self.assertEqual(len(ac['viewer']), 3)

class LDAPTestCase(unittest.TestCase):

    pass
