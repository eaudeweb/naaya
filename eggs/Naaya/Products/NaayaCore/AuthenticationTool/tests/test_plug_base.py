from unittest import mock

from Acquisition import aq_base

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase, capture_events
from Products.NaayaCore.AuthenticationTool.interfaces import \
    IRoleAssignmentEvent


class PlugBaseTest(NaayaTestCase):
    """ role helpers of PlugBase, using a source on the root user folder """

    def afterSetUp(self):
        self.app.acl_users._doAddUser('bob', 'bob', [], [])
        self.app.acl_users._doAddUser('carol', 'carol', [], [])
        auth_tool = self.portal.getAuthenticationTool()
        auth_tool.manageAddSource('acl_users', 'Root users')
        self.source = auth_tool.getSources()[0]

    def request(self):
        request = mock.MagicMock()
        request.AUTHENTICATED_USER.getUserName.return_value = 'admin'
        request.__getitem__.side_effect = {
            'HTTP_REFERER': 'http://localhost/referer'}.__getitem__
        return request

    def test_user_folder(self):
        self.assertEqual(self.source.obj_path, 'acl_users')
        self.assertIs(aq_base(self.source.getUserFolder()),
                      aq_base(self.app.acl_users))
        self.source.obj_path = 'missing'
        self.assertIsNone(self.source.getUserFolder())

    def test_has_user(self):
        self.assertTrue(self.source.has_user('bob'))
        self.assertFalse(self.source.has_user('nobody'))
        auth_tool = self.portal.getAuthenticationTool()
        self.assertEqual(auth_tool.getUserSource('bob'), 'Root users')

    def test_get_local_roles(self):
        self.assertEqual(self.source.getLocalRoles(
            ['Owner', 'Contributor', 'Authenticated', 'Meeting Participant',
             'Meeting Waiting List', 'Administrator']),
            ['Contributor', 'Administrator'])

    def test_add_user_roles(self):
        self.source.addUserRoles('bob', ['Contributor'], 'info')
        self.source.addUserRoles(['bob', 'carol'], 'Administrator')
        self.assertEqual(self.portal.info.get_local_roles_for_userid('bob'),
                         ('Contributor',))
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'),
                         ('Administrator',))
        self.assertEqual(self.portal.get_local_roles_for_userid('carol'),
                         ('Administrator',))

    def test_add_user_roles_errors(self):
        cases = [({'name': [], 'roles': ['Contributor']}, 'No user selected'),
                 ({'name': 'bob', 'roles': []}, 'No roles selected'),
                 ({'name': 5, 'roles': ['Contributor']},
                  'Username selection error'),
                 ({'name': 'bob', 'roles': ['Contributor'],
                   'location': 'missing'}, 'Invalid location path')]
        for kwargs, message in cases:
            with self.assertRaises(ValueError) as cm:
                self.source.addUserRoles(**kwargs)
            self.assertEqual(str(cm.exception), message)

    @capture_events(IRoleAssignmentEvent)
    def test_add_and_revoke_with_request(self, events):
        self.login()
        request = self.request()
        self.source.addUserRoles('bob', ['Contributor'], 'info',
                                 REQUEST=request)
        request.RESPONSE.redirect.assert_called_with(
            'http://localhost/referer')
        self.assertEqual(len(events), 1)
        self.assertEqual((events[0].manager_id, events[0].user_id,
                          events[0].assigned, events[0].unassigned),
                         ('admin', 'bob', ['Contributor'], []))

        request = self.request()
        self.source.revokeUserRoles('bob', 'info', REQUEST=request)
        self.assertEqual(self.portal.info.get_local_roles_for_userid('bob'),
                         ())
        request.RESPONSE.redirect.assert_called_with(
            'http://localhost/referer')
        self.assertEqual(len(events), 2)
        self.assertEqual((events[1].user_id, events[1].assigned,
                          events[1].unassigned, events[1].send_mail),
                         ('bob', [], ['Contributor'], False))
        self.logout()

    def test_revoke_user_roles(self):
        self.source.addUserRoles('bob', ['Contributor'])
        self.source.revokeUserRoles('bob', '/')
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'), ())
        with self.assertRaises(ValueError):
            self.source.revokeUserRoles('bob', 'missing')

    def test_get_users_roles(self):
        self.source.addUserRoles('bob', ['Contributor'], 'info')
        self.source.addUserRoles('bob', ['Administrator'])
        self.source.addUserRoles('carol', ['Owner'], 'info')
        # local users of the portal are not listed for this source
        self.portal.manage_setLocalRoles('user1', ['Administrator'])
        roles = self.source.getUsersRoles(self.source.getUserFolder())
        self.assertEqual(sorted(roles), ['bob'])
        self.assertEqual(sorted(roles['bob']),
                         [(['Administrator'], 'portal'),
                          (['Contributor'], 'portal/info')])

    def test_remove_user(self):
        self.source.addUserRoles('bob', ['Contributor'], 'info')
        self.source.addUserRoles('bob', ['Administrator'])
        self.source.addUserRoles('carol', ['Contributor'], 'info')
        self.assertTrue(self.source.removeUser('bob'))
        self.assertEqual(self.portal.info.get_local_roles_for_userid('bob'),
                         ())
        self.assertEqual(self.portal.get_local_roles_for_userid('bob'), ())
        self.assertEqual(
            self.portal.info.get_local_roles_for_userid('carol'),
            ('Contributor',))
        self.assertIsNone(self.source.removeUser('nobody'))
