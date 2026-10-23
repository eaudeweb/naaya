import unittest

from Products.NaayaBase.NyFolderishVersioning import NyFolderishVersioning


class CompareVersionsTest(unittest.TestCase):

    def setUp(self):
        self.versioning = NyFolderishVersioning()

    def test_same_content(self):
        compare = self.versioning._compare_versions
        self.assertFalse(compare(b'caf\xc3\xa9', 'café'))
        self.assertFalse(compare('café', b'caf\xc3\xa9'))
        self.assertFalse(compare(b'\xff\x00', b'\xff\x00'))

    def test_different_content(self):
        compare = self.versioning._compare_versions
        self.assertTrue(compare(b'abc', b'abd'))
        self.assertTrue(compare('abc', b'abd'))
