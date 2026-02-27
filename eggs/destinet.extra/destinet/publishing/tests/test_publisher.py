from unittest.mock import Mock

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.users import UnrestrictedUser

from naaya.content.url.url_item import addNyURL

from destinet.testing.DestinetTestCase import DestinetTestCase


def loginUnrestricted():
    """ """
    noSecurityManager()
    god = UnrestrictedUser('god', 'god', [], '')
    newSecurityManager(None, god)
    return god


class PublisherTestSuite(DestinetTestCase):

    def setUp(self):
        self.REQUEST = Mock()
        self.REQUEST.RESPONSE = Mock()
        self.redirect = None

        def save_redirect(url):
            self.redirect = url

        self.REQUEST.RESPONSE.redirect = save_redirect
        super(PublisherTestSuite, self).setUp()

    def test_disseminate_url(self):
        addNyURL(self.portal.resources, id='url', title='url',
                 coverage='Georgia, Not Existing', topics=['atopic'],
                 url='http://eaudeweb.ro', contributor='simiamih')
        # Pointer auto-creation was removed in #4463, so the URL should
        # not appear under countries.
        self.assertEqual(getattr(self.portal.countries.southgeorgia,
                                 'url', None), None)
