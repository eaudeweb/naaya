from os import path
from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.LayoutTool.DiskFile import (DiskFile, resolve,
                                                    manage_addDiskFile)

from Products import Naaya as Naaya_module
naaya_module_path = path.dirname(Naaya_module.__file__)
logo_data = open(naaya_module_path + '/skel/layout/left_logo.gif').read()

class DiskFileTest(NaayaTestCase):
    def test_resolve(self):
        self.assertRaises(ValueError, resolve, '')
        self.assertRaises(ValueError, resolve, 'adsf')
        self.assertRaises(ValueError, resolve, 'asdfa:asdfas')
        self.assertRaises(ValueError, resolve, 'asdfa:asd::fas')
        self.assertRaises(ValueError, resolve, 'Products.NaayaCore:events.py')
        self.assertRaises(ValueError, resolve, 'Products.Naaya:NySite.py')
        self.assertEqual(resolve('Products.Naaya:skel/layout/la/la/la'),
                         naaya_module_path + '/skel/layout/la/la/la')

    def test_render(self):
        disk_file = DiskFile('left_logo.gif', 'Products.Naaya:skel/layout/left_logo.gif')

        self.assertEqual(disk_file._get_mime_type(), 'image/gif')
        self.assertEqual(disk_file._get_data(), logo_data)


class DiskFileBrowserTest(NaayaFunctionalTestCase):
    def afterSetUp(self):
        skin = self.portal.portal_layout.getCurrentSkin()
        manage_addDiskFile(skin, 'test-logo.gif',
                           'Products.Naaya:skel/layout/left_logo.gif')
        transaction.commit()

    def test_get(self):
        self.browser.go('http://localhost/portal/'
                        'portal_layout/skin/test-logo.gif')
        self.assertEqual(self.browser.get_html(), logo_data, "bad content")
        self.assertEqual(self.browser_get_header('content-type'), 'image/gif')
