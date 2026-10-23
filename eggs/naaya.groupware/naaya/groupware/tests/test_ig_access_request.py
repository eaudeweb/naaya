import email
from unittest.mock import MagicMock as Mock, patch
import transaction
from Products.Naaya.NyFolder import addNyFolder
from naaya.groupware.tests import GWFunctionalTestCase, GWTestCase

LDAP_ROLES = [
    {'id': 'places', 'parent': 'top', 'children': ['places-atm'],
     'description': 'Places'},
    {'id': 'places-atm', 'parent': 'places', 'children': [],
     'description': 'ATM'},
    {'id': 'places-bank', 'parent': 'places', 'children': [],
     'description': 'Bank'},
]


class MockedSource(Mock):
    """ Mocked ldap source """
    def get_user_info(self, user):
        info = Mock()
        info.email = 'x@example.com'
        return info

    def getUserFullName(self, userid, acl_folder):
        return None


class SourceMixin(object):

    def mocked_source(self):
        # Users come from the root user folder instead of LDAP
        source = MockedSource()
        source.getUserFolder.return_value = self.portal.aq_parent.acl_users
        return source


class IGRequestTestCase(SourceMixin, GWFunctionalTestCase):

    def afterSetUp(self):
        # Create a no role user so that we can request a role
        self.portal.aq_parent.acl_users._doAddUser('norole', 'norole', [], '')
        transaction.commit()

        # Make this portal restricted so the request form can be displayed
        self.portal.toggle_portal_restricted(True)
        # Mock the sources so we don't connect to a ldap server
        self.p = patch(
            'Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
            'AuthenticationTool.getSources',
            Mock(return_value=[self.mocked_source()]))
        self.p.start()

    def beforeTearDown(self):
        self.p.stop()

    def test_already_member(self):
        """ Admin is already a member of the portal so it doesn't require
        an ig access

        """

        self.browser_do_login('admin', '')
        self.browser.go(self.portal.absolute_url() + '/request_ig_access_html')
        self.assertEqual(self.browser.get_code(), 200)
        # Admin has every role, so only Meeting Observer can be requested
        html = self.browser.get_html()
        self.assertIn('id="observer_role"', html)
        for role in ('Viewer', 'Reviewer', 'Contributor'):
            self.assertNotIn('value="%s"' % role, html)

    def test_role_choices_for_norole(self):
        self.browser_do_login('norole', 'norole')
        self.browser.go(self.portal.absolute_url() + '/request_ig_access_html')
        html = self.browser.get_html()
        for role in ('Reviewer', 'Contributor'):
            self.assertIn('value="%s"' % role, html)

    def test_send_request(self):
        """ Get the page with the request form and submit it with a normal
        request. After the request is submitted there should be an e-mail in
        the outbox. Besides the e-mail there also should be an action log in
        action logger.

        """

        self.browser_do_login('norole', 'norole')
        self.browser.go(self.portal.absolute_url() + '/request_ig_access_html')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'role')
        self.browser.clicked(form, field)
        form['role'] = 'Reviewer'
        self.browser.submit()
        self.assertTrue('The Interest Group administrators have been notified '
                        'of your access request' in self.browser.get_html())
        mail_outbox = dict(self.mail_log)['sendmail']
        self.assertEqual(mail_outbox['to'][0], 'site.admin@example.com')
        # There should be something about this user in the e-mail
        self.assertTrue('Username: norole' in mail_outbox['message'])

        action_logger = self.portal.getActionLogger()
        self.assertEqual(action_logger[1].user, 'norole')
        self.assertEqual(action_logger[1].role, 'Reviewer')
        body = email.message_from_string(mail_outbox['message'])\
            .get_payload(decode=True).decode('utf-8')
        self.assertIn('review_ig_request?key=%s' % action_logger[1].key, body)


class IGRequestUnitTestCase(SourceMixin, GWTestCase):
    """ request_ig_access called directly """

    def afterSetUp(self):
        self.app.acl_users._doAddUser('norole', 'norole', [], '')
        addNyFolder(self.portal, 'docs', title='Docs', submitted=1)
        self.p = patch(
            'Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
            'AuthenticationTool.getSources',
            Mock(return_value=[self.mocked_source()]))
        self.p.start()

    def beforeTearDown(self):
        self.p.stop()

    def request(self, **form):
        request = Mock()
        request.form = form
        request.AUTHENTICATED_USER.getId.return_value = 'norole'
        return request

    def test_archived(self):
        from zExceptions import BadRequest
        self.portal.portal_is_archived = True
        self.assertRaises(BadRequest, self.portal.request_ig_access,
                          self.request(role='Viewer'))

    def test_no_role(self):
        request = self.request(role='')
        self.portal.request_ig_access(request)
        request.RESPONSE.redirect.assert_called_once_with(
            request.HTTP_REFERER)
        self.assertEqual(len(self.portal.getActionLogger()), 0)

    def test_location_in_subfolder(self):
        request = self.request(role='Contributor',
                               location_url=self.portal['docs'].absolute_url()
                               + '/index_html')
        self.portal.request_ig_access(request)
        (_id, entry), = self.portal.getActionLogger().items()
        # requests are made for the whole IG, unless inside a meeting
        self.assertEqual(entry.location, '/%s/' % self.portal.getId())
        self.assertEqual(entry.role, 'Contributor')
        self.assertEqual(entry.location_url, self.portal.absolute_url())

    def test_bytes_names_in_email(self):
        from naaya.groupware.groupware_site import _to_text
        self.assertEqual(_to_text(b'Ana-Maria \xc8\x98t'), 'Ana-Maria Șt')
        self.assertEqual(_to_text(b'Fran\xe7ois'), 'Fran\xe7ois')
        self.assertEqual(_to_text('Ion'), 'Ion')


class IGReviewTestCase(SourceMixin, GWFunctionalTestCase):
    """ Review process """

    def afterSetUp(self):
        # Create a no role user so that we can request a role
        self.portal.aq_parent.acl_users._doAddUser('norole', 'norole', [], '')
        self.action_logger = self.portal.getActionLogger()
        # Create a log so that we can match a key
        self.action_logger.create(user='norole',
                                  location_title='gw_portal',
                                  location='',
                                  key='4db91157307c2c817b6a8695974987d2',
                                  role='Contributor',
                                  type='IG role request',
                                  location_url=self.portal.absolute_url())
        transaction.commit()

        # Mock the sources so we don't connect to a ldap server
        self.p = patch(
            'Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
            'AuthenticationTool.getSources',
            Mock(return_value=[self.mocked_source()]))
        self.p.start()
        # The first review page reads the user and the roles from LDAP
        agent = Mock()
        agent.user_info.return_value = dict.fromkeys(
            ('first_name', 'last_name', 'email', 'phone', 'mobile', 'fax',
             'postal_address'), '')
        agent.user_info.return_value['uid'] = 'norole'
        client = Mock()
        client.return_value.roles_list_in_ldap.return_value = LDAP_ROLES
        self.patches = [
            patch('naaya.groupware.groupware_site.agent_from_site',
                  Mock(return_value=agent)),
            patch('naaya.groupware.groupware_site.ProfileClient', client)]
        for p in self.patches:
            p.start()

    def beforeTearDown(self):
        self.p.stop()
        for p in self.patches:
            p.stop()

    def test_review_request_fail(self):
        """ An invalid key should display an error message """

        key = 'somekey'
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        self.assertTrue('Key %s not found' % key in self.browser.get_html())

    def test_review_request(self):
        """ Generate a request then get the review form"""

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        html = self.browser.get_html()
        self.assertTrue('Review IG access request' in html)
        # the leaf LDAP roles, with alternating row classes
        self.assertIn('class="even places" id="row_places-atm"', html)
        self.assertIn('class="odd places" id="row_places-bank"', html)
        self.assertNotIn('id="row_places"', html)

    def test_grant(self):
        """ Grant the role user has requested """

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser_do_login('admin', '')
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'grant')
        self.browser.clicked(form, field)
        with patch('naaya.groupware.groupware_site.notify') as notify:
            self.browser.submit()
        self.assertEqual(action_logger[2].action, 'Granted')
        auth_tool = self.portal.getAuthenticationTool()
        add_roles = auth_tool.getSources()[0].addUserRoles
        add_roles.assert_called_once()
        kwargs = add_roles.call_args.kwargs
        self.assertEqual((kwargs['name'], kwargs['location'], kwargs['roles'],
                          kwargs['send_mail']),
                         ('norole', '', 'Contributor', False))
        event, = notify.call_args.args
        self.assertEqual((event.manager_id, event.user_id, event.assigned,
                          event.unassigned),
                         ('admin', 'norole', ['Contributor'], []))
        self.assertEqual(len(action_logger), 2)

    def test_reject(self):
        """ Reject without a reason """

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'reject')
        self.browser.clicked(form, field)
        self.browser.submit()
        self.assertEqual(action_logger[2].action, 'Rejected')
        self.assertEqual(len(action_logger), 2)

    def test_reject_reason(self):
        """ Reject with a reason """

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'reject')
        self.browser.clicked(form, field)
        form['reason'] = 'Some reason'
        self.browser.submit()
        self.assertEqual(action_logger[2].action, 'Rejected')
        self.assertEqual(action_logger[2].reason, 'Some reason')
        self.assertEqual(len(action_logger), 2)

    def test_reject_reason_email(self):
        """ Reject with a reason and notify the user with an e-mail """

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'reject')
        self.browser.clicked(form, field)
        form['reason'] = 'Some reason'
        form['send_mail'] = ['1']
        self.browser.submit()

        # Should contain the reason
        self.assertTrue('Some reason' in
                        dict(self.mail_log)['sendmail']['message'])

    def test_2_times(self):
        """ Try to use the same key twice and fail in doing so """

        action_logger = self.portal.getActionLogger()
        action_logger.append(action_logger[1])
        transaction.commit()

        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        self.assertIn('An administrator already processed this request',
                      self.browser.get_html())


class RelinquishTestCase(SourceMixin, GWFunctionalTestCase):

    def afterSetUp(self):
        self.source = self.mocked_source()
        self.source.removeUser.return_value = True
        self.p = patch(
            'Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
            'AuthenticationTool.getSources',
            Mock(return_value=[self.source]))
        self.p.start()

    def beforeTearDown(self):
        self.p.stop()

    def test_relinquish_pas_user(self):
        from Products.PluggableAuthService.PropertiedUser import (
            PropertiedUser)
        request = Mock()
        request.__getitem__.side_effect = {'REQUEST_METHOD': 'POST'}.get
        request.AUTHENTICATED_USER = PropertiedUser('norole', 'norole')
        self.portal.relinquish_membership(request)
        self.source.removeUser.assert_called_once_with('norole')
        self.assertTrue(request.RESPONSE.redirect.call_args[0][0].endswith(
            '/relinquish_membership_html?done=success'))
