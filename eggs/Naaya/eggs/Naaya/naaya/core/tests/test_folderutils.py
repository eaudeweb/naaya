from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.core import folderutils

class TestOrderFolder(NaayaTestCase):
    def afterSetUp(self):
        self.portal.manage_addFolder('folder1')
        self.portal.folder1.manage_addFolder('folder11')
        self.portal.folder1.manage_addFolder('folder12')
        self.portal.folder1.manage_addFolder('folder13')

    def test_basic(self):
        """ Let's create a folder with a few objects and change their order """
        order_seq = ['folder11', 'folder13', 'folder12']
        folderutils.sort_folder(self.portal.folder1, order_seq)
        self.assertEqual(self.portal.folder1.objectIds(), order_seq)

    def test_unchanged(self):
        """ Nothing changes """
        order_seq = self.portal.folder1.objectIds()
        folderutils.sort_folder(self.portal.folder1, order_seq)
        self.assertEqual(self.portal.folder1.objectIds(), order_seq)

    def test_incomplete(self):
        """ Some ids from the folder are missing in the call. This means that
        the folder must be reordered and the missing ids must be put at the
        end."""

        order_seq = ['folder13', 'folder12']
        folderutils.sort_folder(self.portal.folder1, order_seq)
        self.assertEqual(self.portal.folder1.objectIds(),
                order_seq + ['folder11'])


