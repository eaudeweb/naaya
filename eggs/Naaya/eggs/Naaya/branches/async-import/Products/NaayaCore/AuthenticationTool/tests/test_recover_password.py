from datetime import timedelta
import transaction
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

MAIL_OK_MSG = "e-mail message has been sent"
PLEASE_ENTER_NEW_PASS_MSG = "Please enter a new password"
PASSWORD_CHANGE_OK_MSG = "password has been changed successfully"
TOKEN_EXPIRED_MSG = ("Your password change link is invalid - it probably"
                     " expired. Please try again.")

class RecoverPasswordTest(NaayaFunctionalTestCase):
    def _logged_mails(self):
        for entry_type, entry_data in self.mail_log:
            if entry_type == 'sendmail':
                yield entry_data

    def test_password_email(self):
        self.browser.go('http://localhost/portal/login_html')
        assert ( 'href="http://localhost/portal/acl_users/recover_password"'
                 in self.browser.get_html() )

        self.browser.go('http://localhost/portal/acl_users/recover_password')
        form = self.browser.get_form('recover-password')
        form['email'] = 'no-such-user@example.com'
        self.browser.clicked(form, form.find_control('email'))
        self.browser.submit()
        assert MAIL_OK_MSG not in self.browser.get_html()
        assert ( 'E-mail address not found: "no-such-user@example.com"'
                 in self.browser.get_html() )

        self.browser.go('http://localhost/portal/acl_users/recover_password')
        form = self.browser.get_form('recover-password')
        form['email'] = 'reviewer@example.com'
        self.browser.clicked(form, form.find_control('email'))
        self.browser.submit()
        assert MAIL_OK_MSG in self.browser.get_html()

        sent_mails = list(self._logged_mails())
        assert len(sent_mails) == 1
        email = sent_mails[0]
        assert email['to'] == ['reviewer@example.com']
        assert 'click on the link below' in email['message']

    def test_click_email_link(self):
        recover_password = self.portal.acl_users.recover_password
        token = recover_password._new_token('contributor')
        transaction.commit()

        self.browser.go('http://localhost/portal/acl_users/recover_password'
                        '/confirm?token=' + token)
        assert PLEASE_ENTER_NEW_PASS_MSG in self.browser.get_html()

        form = self.browser.get_form('enter-new-password')
        form['new_password'] = 'asdf'
        form['new_password_confirm'] = 'asdf2'
        self.browser.clicked(form, form.find_control('new_password_confirm'))
        self.browser.submit()
        assert "Passwords do not match" in self.browser.get_html()

        form = self.browser.get_form('enter-new-password')
        form['new_password'] = 'my-shiny-new-pass'
        form['new_password_confirm'] = 'my-shiny-new-pass'
        self.browser.clicked(form, form.find_control('new_password_confirm'))
        self.browser.submit()
        assert PASSWORD_CHANGE_OK_MSG in self.browser.get_html()

        assert ( self.portal.acl_users.data['contributor'].__ ==
                 'my-shiny-new-pass' )

    def test_bad_token(self):
        # bad token in "confirm" page
        self.browser.go('http://localhost/portal/acl_users/recover_password'
                        '/confirm?token=nosuchtoken')
        assert PLEASE_ENTER_NEW_PASS_MSG not in self.browser.get_html()
        assert TOKEN_EXPIRED_MSG in self.browser.get_html()

        # bad token in "set_new_password_html" page
        self.browser.go('http://localhost/portal/acl_users/recover_password'
                        '/set_new_password_html?token=nosuchtoken')
        form = self.browser.get_form('enter-new-password')
        form['new_password'] = 'my-evil-pass'
        form['new_password_confirm'] = 'my-evil-pass'
        self.browser.clicked(form, form.find_control('new_password_confirm'))
        self.browser.submit()
        assert PASSWORD_CHANGE_OK_MSG not in self.browser.get_html()
        assert TOKEN_EXPIRED_MSG in self.browser.get_html()

    def test_password_changer(self):
        # the old username/password should work
        self.browser_do_login('contributor', 'contributor')
        self.browser_do_logout()

        # change the password
        self.portal.acl_users.recover_password._set_password('contributor', 'X')
        transaction.commit()

        # the old username/password should fail
        self.assertRaises(AssertionError, self.browser_do_login,
                          'contributor', 'contributor')

        # but the new one should work
        self.browser_do_login('contributor', 'X')
        self.browser_do_logout()

    def test_cron(self):
        recover_password = self.portal.acl_users.recover_password
        token_map = recover_password._get_token_map()

        token1 = recover_password._new_token('contributor')
        token2 = recover_password._new_token('contributor')
        assert len(token_map) == 2

        token_map[token1].create_time -= timedelta(days=2)
        self.portal.heartbeat_work()

        assert len(token_map) == 1
        assert list(token_map.keys()) == [token2]
