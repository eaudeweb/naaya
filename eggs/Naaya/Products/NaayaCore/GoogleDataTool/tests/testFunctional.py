from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase


class GoogleDataToolFunctionalTestCase(NaayaFunctionalTestCase):
    """ Functional TestCase for GoogleData tool """

    def test_main(self):
        self.browser_do_login('admin', '')
        self.browser.go(
            'http://localhost/portal/portal_statistics/admin_verify')
        self.assertTrue(
            '<h1>Portal statistics</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmVerify')
        expected_controls = set(['ga_id', 'gw_verify'])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
                        'Missing form controls: %s' % repr(expected_controls -
                                                           found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'ga_id'))
        form['ga_id'] = 'UA-12345-67'
        form['gw_verify'] = ('<meta name="google-site-verification" '
                             'content="test-code" />')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('Saved changes.' in html)
        self.browser_do_logout()

        self.browser.go('http://localhost/portal')
        soup = BeautifulSoup(self.browser.get_html())

        # check if the GoogleWebmaster meta tag is corectly placed in the
        # <head> section, before the first <body> section.
        head = soup.html.head
        self.failUnless(head.find('meta',
                                  attrs={'name': 'google-site-verification',
                                         'content': 'test-code'}))

        # check if the GoogleAnalytics javascript is corectly placed in the
        # <head> section, before the closing </head> tag.
        script = head.findAll('script')[-2]
        self.assertTrue(script.text.find('UA-12345-67') > -1)
