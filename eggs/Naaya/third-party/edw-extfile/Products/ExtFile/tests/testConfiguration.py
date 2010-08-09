#
# Configuration tests
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile import configuration
from Products.ExtFile.ExtFile import guess_extension


class TestConfiguration(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        configuration.loadfile(configuration.EXAMPLE_INI)

    def testConfiguration(self):
        config = configuration.config
        self.assertEqual(config.location, ['static', 'reposit'])
        self.assertEqual(config.umask, 022)
        self.assertEqual(config.mode, 'sliced-hash')
        self.assertEqual(config.case, 'normalize')
        self.assertEqual(config.zodb_path, 'physical')
        self.assertEqual(config.slice_width, 1)
        self.assertEqual(config.slice_depth, 2)
        self.assertEqual(config.custom_method, 'getExtFilePath')
        self.assertEqual(config.file_format, '%n%c%e')
        self.assertEqual(config.extensions, 'mimetype-replace')
        self.assertEqual(config.copy_of_protection, 'allow')
        self.assertEqual(config.undo_policy, 'backup-on-delete')

    def testLegacyConfiguration(self):
        self.assertEqual(configuration.REPOSITORY_PATH, ['static', 'reposit'])
        self.assertEqual(configuration.REPOSITORY_UMASK, 022)
        self.assertEqual(configuration.REPOSITORY, configuration.SLICED_HASH)
        self.assertEqual(configuration.NORMALIZE_CASE, configuration.NORMALIZE)
        self.assertEqual(configuration.ZODB_PATH, configuration.PHYSICAL)
        self.assertEqual(configuration.SLICE_WIDTH, 1)
        self.assertEqual(configuration.SLICE_DEPTH, 2)
        self.assertEqual(configuration.CUSTOM_METHOD, 'getExtFilePath')
        self.assertEqual(configuration.FILE_FORMAT, '%n%c%e')
        self.assertEqual(configuration.REPOSITORY_EXTENSIONS, configuration.MIMETYPE_REPLACE)
        self.assertEqual(configuration.COPY_OF_PROTECTION, configuration.DISABLED)
        self.assertEqual(configuration.UNDO_POLICY, configuration.BACKUP_ON_DELETE)

    def testExtensionGuessing(self):
        self.assertEqual(guess_extension('text/plain'), '.txt')
        self.assertEqual(guess_extension('application/octet-stream'), '.exe')
        self.assertEqual(guess_extension('image/tiff'), '.tif')
        self.assertEqual(guess_extension('image/jpeg'), '.jpg')
        self.assertEqual(guess_extension('audio/x-aiff'), '.aif')
        self.assertEqual(guess_extension('audio/mpeg'), '.mp3')
        self.assertEqual(guess_extension('video/quicktime'), '.mov')
        self.assertEqual(guess_extension('video/mpeg'), '.mpg')
        self.assertEqual(guess_extension('text/rtf'), '.rtf')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfiguration))
    return suite

