""" utils.utGenerateZip """
import tempfile
import unittest
import zipfile
from io import BytesIO
from unittest.mock import Mock

from Products.NaayaCore.managers.utils import utils


class Item(object):
    def __init__(self, id, data):
        self.id, self.data = id, data

    def getId(self):
        return self.id

    def get_size(self):
        return len(self.data)

    def getZipData(self):
        return self.data


class GenerateZipTest(unittest.TestCase):

    def test_zip_content_and_temp_dir_unchanged(self):
        before = tempfile.tempdir
        content = utils().utGenerateZip('photos', [Item('a.txt', b'abc')],
                                        Mock())
        self.assertEqual(tempfile.tempdir, before)
        with zipfile.ZipFile(BytesIO(content)) as zf:
            self.assertEqual(zf.read('photos/a.txt'), b'abc')
