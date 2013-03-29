import transaction
from naaya.groupware.tests import GWFunctionalTestCase

class IGWebExRequest(GWFunctionalTestCase):

    def afterSetUp(self):
        #Create a no role user so that we can request a role
        self.portal.aq_parent.acl_users._doAddUser('norole', 'norole', [], '')
        transaction.commit()

        #Make this portal restricted so the request form can be displayed
        self.portal.toggle_portal_restricted(True)
        #Mock the sources so we don't connect to a ldap server
        self.p = patch(
            'Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
            'AuthenticationTool.getSources',
            Mock(return_value=[MockedSource()]))
        self.p.__enter__()

    def beforeTearDown(self):
        self.p.__exit__()

    def test_already_member(self):
        """ Admin is already a member of the portal so it doesn't require
        an ig access

        """

        self.browser_do_login('admin', '')
        self.browser.go(self.portal.absolute_url() + '/request_ig_access_html')
        self.assertTrue('You are already a member of this interest group' in
                        self.browser.get_html())

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
        self.browser.submit()
        self.assertTrue('The Group Leader has been notified of your access'
                        ' request' in self.browser.get_html())
        mail_outbox = dict(self.mail_log)['sendmail']
        self.assertEqual(mail_outbox['to'][0], 'site.admin@example.com')
        #There should be something about this user in the e-mail
        self.assertTrue('Username: norole' in mail_outbox['message'])

        action_logger = self.portal.getActionLogger()
        self.assertEqual(action_logger[1].user, 'norole')

class IGReviewTestCase(GWFunctionalTestCase):
    """ Review process """

    def afterSetUp(self):
        #Create a no role user so that we can request a role
        self.action_logger = self.portal.getActionLogger()
        #Create a log so that we can match a key
        self.action_logger.create(user='norole',
                             location_title='gw_portal',
                             location='',
                             key='4db91157307c2c817b6a8695974987d2',
                             role='Contributor',
                             type='IG role request',
                             location_url=self.portal.absolute_url())
        transaction.commit()

        #Mock the sources so we don't connect to a ldap server
        self.p = patch(
            'Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
            'AuthenticationTool.getSources',
            Mock(return_value=[MockedSource()]))
        self.p.__enter__()

    def beforeTearDown(self):
        self.p.__exit__()

    def test_review_request_fail(self):
        """ An invalid key should display an error message """

        key = 'somekey'
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        self.assertTrue('Key %s not found' % key
                in self.browser.get_html())

    def test_review_request(self):
        """ Generate a request then get the review form"""

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        self.assertTrue('Review IG access request' in self.browser.get_html())

    def test_grant(self):
        """ Grant the role user has requested """

        action_logger = self.portal.getActionLogger()
        key = action_logger[1].key
        self.browser.go(self.portal.absolute_url() +
                        '/review_ig_request?key=%s' % key)
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'grant')
        self.browser.clicked(form, field)
        self.browser.submit()
        self.assertTrue('Role has been granted' in self.browser.get_html())
        auth_tool = self.portal.getAuthenticationTool()
        self.assertTrue(auth_tool.getSources()[0].addUserRoles.called)
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
        self.assertTrue('Request has been rejected' in self.browser.get_html())
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
        self.assertTrue('Request has been rejected' in self.browser.get_html())
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

        #Should contain the reason
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
        self.assertTrue('Key %s has already been used' % key in
                    self.browser.get_html())
