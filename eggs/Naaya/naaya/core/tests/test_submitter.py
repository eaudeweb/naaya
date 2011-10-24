import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder

def captcha_in_html(html):
    if 'recaptcha_challenge_field' in html:
        return True
    else:
        return False

def nameandemail_in_html(html):
    if 'Your name' in html and 'Your e-mail address' in html:
        return True
    else:
        return False

class SubmitterInfoTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder',
                    contributor='contributor', submitted=1)
        self.portal.myfolder._Naaya___Skip_Captcha_Permission = ['Contributor']
        self.portal.myfolder._Naaya___Add_Naaya_URL_objects_Permission = [
            'Anonymous', 'Administrator', 'Contributor']

        self.recaptcha_public_key = self.portal.recaptcha_public_key
        self.recaptcha_private_key = self.portal.recaptcha_private_key
        self.portal.recaptcha_public_key = '1'
        self.portal.recaptcha_private_key = '1'

        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.recaptcha_public_key = self.recaptcha_public_key
        self.portal.recaptcha_private_key = self.recaptcha_private_key
        transaction.commit()

    def test_logged_in_skipcaptcha(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        self.assertFalse(captcha_in_html(self.browser.get_html()))

    def test_logged_in_no_skipcaptcha(self):
        self.portal.myfolder._Naaya___Skip_Captcha_Permission = tuple()
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        self.assertTrue(captcha_in_html(self.browser.get_html()))
        self.browser_do_logout()

    def test_logged_in_no_nameandemail(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        self.assertFalse(nameandemail_in_html(self.browser.get_html()))
        self.browser_do_logout()

    def test_not_logged_in_nameandemail(self):
        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        self.assertTrue(nameandemail_in_html(self.browser.get_html()))

    def test_save_nameandemail(self):
        self.portal.myfolder._Naaya___Skip_Captcha_Permission = ['Anonymous']
        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:ustring'] = 'testurl'
        form['submitter-name'] = "Gigel Xulescu"
        form['submitter-email'] = "gigel@example.com"
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.assertTrue('testurl' in self.portal['myfolder'].objectIds())
        ob = self.portal['myfolder']['testurl']
        self.assertEqual(ob.submitter_info, {'name': "Gigel Xulescu",
                                              'email': "gigel@example.com"})

    def test_missing_nameandemail(self):
        self.portal.myfolder._Naaya___Skip_Captcha_Permission = ['Anonymous']
        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/url_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:ustring'] = 'testurl'
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.assertFalse('testurl' in self.portal['myfolder'].objectIds())
        html = self.browser.get_html()
        self.assertTrue("Submitter name is mandatory" in html)
        self.assertTrue("Submitter email is mandatory" in html)
