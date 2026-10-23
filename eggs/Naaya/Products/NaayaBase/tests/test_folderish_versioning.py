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

    def test_blob_streams(self):
        import io

        class Blob(object):
            def __init__(self, data):
                self.stream = io.BytesIO(data)

            def index_html(self):
                return self.stream
        compare = self.versioning._compare_versions
        blob1, blob2 = Blob(b'data'), Blob(b'data')
        self.assertFalse(compare(blob1, blob2))
        self.assertTrue(compare(Blob(b'data'), Blob(b'other')))
        self.assertTrue(blob1.stream.closed and blob2.stream.closed)
