import hashlib
import os
import shutil
import tempfile
import unittest
from io import BytesIO
from types import SimpleNamespace

from naaya.content.bfile.updates import update_fix_nyblobs
from naaya.content.bfile.updates.update_nyfile2nyblob import Import

DATA = b'\xff\xfe\x00 binary \xc8'


class FixNyBlobsTest(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder)
        with open(os.path.join(self.folder, 'report.2.pdf.undo'), 'wb') as f:
            f.write(DATA)

    def test_hashfile(self):
        self.assertEqual(
            update_fix_nyblobs.hashfile(os.path.join(self.folder,
                                                     'report.2.pdf.undo')),
            hashlib.md5(DATA).digest())

    def test_get_content(self):
        script = update_fix_nyblobs.UpdateFixNyBlobFile.__new__(
            update_fix_nyblobs.UpdateFixNyBlobFile)
        content = script.get_content(self.folder, 'report.2.pdf.undo')
        self.assertEqual(content.read(), DATA)
        self.assertEqual(content.filename, 'report.2.pdf')
        self.assertEqual(content.headers, {'content-type': 'application/pdf'})

    def test_version_order(self):
        names = ['a.10.txt', 'a.2.txt', 'a.txt', 'a.1.txt']
        self.assertEqual(sorted(names, key=update_fix_nyblobs.inter),
                         ['a.txt', 'a.1.txt', 'a.2.txt', 'a.10.txt'])


class Nyfile2NyblobImportTest(unittest.TestCase):

    def test_versions(self):
        importer = Import.__new__(Import)
        importer.context = SimpleNamespace()
        version = BytesIO(DATA)
        version.filename = 'data.bin'
        importer.versions = [version]
        self.assertEqual(len(importer.context._versions), 1)
        blob_file = importer.context._versions[0]
        self.assertEqual(blob_file.filename, 'data.bin')
        with blob_file.open() as f:
            self.assertEqual(f.read(), DATA)
