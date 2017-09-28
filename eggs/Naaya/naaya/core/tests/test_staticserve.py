import os
from unittest import TestSuite, makeSuite

from Globals import package_home

from naaya.core.StaticServe import StaticServeFromFolder
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from naaya.content.document import NyDocument


class StaticServeFromFolderTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        NyDocument.test_static_serve = StaticServeFromFolder('static_serve', globals(), cache=False)

    def beforeTearDown(self):
        del NyDocument.test_static_serve

    def test_a_html(self):
        file_path = os.path.join(package_home(globals()), 'static_serve/a.html')
        fd = open(file_path)
        read_data = fd.read()
        fd.close()

        url = 'http://localhost/portal/info/contact/test_static_serve/a.html'
        self.browser.go(url)
        server_data = self.browser.get_html()

        self.assertEqual(read_data, server_data)
