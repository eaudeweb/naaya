import unittest
import mock
import os.path

from edw.circaimport import ui
from edw.circaimport.circaredirect import circa_redirect


class CircaRedirectTests(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('edw.circaimport.circaredirect.ui.upload_prefix',
                                  os.path.dirname(__file__))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def assert_redirect(self, GET, expected_redirect):
        request = mock.Mock()
        request.form = GET
        circa_redirect(mock.Mock(), request)
        request.RESPONSE.redirect.assert_called_with(expected_redirect)

    def test_home_redirect(self):
        self.assert_redirect({'id': 'gemet', 'type': 'home'},
                             'http://forum.eionet.europa.eu/gemet')
        self.assert_redirect({'id': 'gemet'},
                             'http://forum.eionet.europa.eu/gemet')
        self.assert_redirect({'id': 'leac', 'type': 'home'},
                             'http://projects.eionet.europa.eu/etc-leac')
        self.assert_redirect({'id': 'nrcobsolete', 'type': 'home'},
                             'http://archives.eionet.europa.eu/nrc-obsolete')
        self.assert_redirect({'id': 'unregistered', 'type': 'home'},
                             'http://forum.eionet.europa.eu/unregistered')

    def test_directory_redirect(self):
        self.assert_redirect({'id': 'gemet', 'type': 'directory'},
                             'http://forum.eionet.europa.eu/gemet/member_search')
        self.assert_redirect({'id': 'leac', 'type': 'directory'},
                             'http://projects.eionet.europa.eu/etc-leac/member_search')
        self.assert_redirect({'id': 'nrcobsolete', 'type': 'directory'},
                             'http://archives.eionet.europa.eu/nrc-obsolete/member_search')
        self.assert_redirect({'id': 'unregistered', 'type': 'directory'},
                             'http://forum.eionet.europa.eu/unregistered/member_search')

    def test_library_redirect(self):
        self.assert_redirect({'id': 'gemet', 'type': 'library'},
                             'http://forum.eionet.europa.eu/gemet/library')
        self.assert_redirect({'id': 'leac', 'type': 'library'},
                             'http://projects.eionet.europa.eu/etc-leac/library')
        self.assert_redirect({'id': 'leac', 'type': 'library',
                              'path': '/folder/subfolder/document'},
                             'http://projects.eionet.europa.eu/etc-leac/library/folder/subfolder/document')
