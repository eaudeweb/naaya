
# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web

import re
from unittest import TestSuite, makeSuite
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class GoogleDataToolFunctionalTestCase(NaayaFunctionalTestCase):
    """ Functional TestCase for GoogleData tool """

    def test_main(self):

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/portal_statistics/admin_verify')
        self.assertTrue('<h1>Portal statistics</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmVerify')
        expected_controls = set(['ga_verify', 'gw_verify'])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'ga_verify'))
        form['ga_verify'] = '<script type="text/javascript">var test;</script>'
        form['gw_verify'] = '<meta name="google-site-verification" content="test-code" />'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('Saved changes.' in html)

        self.browser.go('http://localhost/portal')
        soup = BeautifulSoup(self.browser.get_html())

        #check if the GoogleWebmaster meta tag is corectly placed in the <head> section, before the first <body> section.
        head = soup.html.head
        self.failUnless(head.find('meta', attrs={'name':'google-site-verification', 'content': 'test-code'}))

        #check if the GoogleAnalytics javascript is corectly placed in the <head> section, before the closing </head> tag.
        script = head.findAll('script', attrs={'type':'text/javascript'})[-1]
        self.assertEquals(script.text, 'var test;')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(GoogleDataToolFunctionalTestCase))
    return suite
