import re
from lxml.html.soupparser import fromstring

from destinet.testing.DestinetTestCase import (DestinetTestCase,
                                               DestinetFunctionalTestCase)


class RegistrationTestCase(DestinetTestCase):

    def test_contact_created(self):
        pass

    def test_form(self):
        self.portal.REQUEST.SESSION = {}
        create_account = self.portal.createaccount_html(self.portal.REQUEST)
        dom = fromstring(re.sub(r'\s+', ' ', create_account))
        h1 = dom.xpath('//h1')
        self.assertEqual(h1[0].text, 'DestiNet account application')