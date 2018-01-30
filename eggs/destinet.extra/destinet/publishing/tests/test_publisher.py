from mock import Mock
import logging
from tempfile import NamedTemporaryFile

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser

from naaya.content.url.url_item import addNyURL

import destinet.publishing
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
        # Logger setup for testing:
        logger = logging.getLogger(destinet.publishing.subscribers.__name__)
        self.logfile = NamedTemporaryFile()
        handler = logging.FileHandler(self.logfile.name)
        logger.addHandler(handler)

    def tearDown(self):
        self.logfile.close()

    def test_disseminate_url(self):
        addNyURL(self.portal.resources, id='url', title='url',
                 coverage='Georgia, Not Existing', topics=['atopic'],
                 url='http://eaudeweb.ro', contributor='simiamih')
        self.assertEqual(getattr(self.portal.countries.southgeorgia,
                                 'url', None), None)

        log_content = self.logfile.read()
        self.assertTrue(
            "Country 'Not Existing' not found in destinet countries"
            in log_content)
