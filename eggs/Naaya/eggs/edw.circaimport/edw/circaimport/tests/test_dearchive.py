import os.path
import unittest
import tempfile

from App.config import getConfiguration

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from edw.circaimport import dearchive


class DearchiveTestSuite(unittest.TestCase):

    def test_catch_zexp_path(self):
        path = '/var/local/forum/zope-instance/feedback-report.zexp'
        message = '<em>some-id</em> successfully exported to <em>%s</em>' % path
        self.assertEqual(dearchive.manage_main_catch_path('', '', message, ''),
                         path)


class DearchiveNaayaTestSuite(NaayaTestCase):

    def test_write_zexp(self):
        config = getConfiguration()
        ob = self.portal.info
        path = dearchive.write_zexp(ob)
        self.assertEqual(path, os.path.join(config.clienthome,
                                            '%s.zexp' % ob.getId()))
        self.assertTrue(os.path.isfile(path))

    def test_write_load_zexp(self):
        ob = self.portal.info
        path = dearchive.write_zexp(ob)
        object_ids = ob.objectIds()
        self.portal._delObject('info')
        dearchive.load_zexp(path, self.portal)
        self.assertEqual(self.portal.info.objectIds(), object_ids)
