import unittest
#from Products.Naaya.NyFolder import NyFolder, manage_addFolder
import transaction
from ZODB.MappingStorage import MappingStorage
from ZODB.DB import DB

from OFS.Folder import Folder, manage_addFolder
from naaya.core import folderutils
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase


class TestOrderFolder(unittest.TestCase):

    def setUp(self):
        self.folder = Folder('folder1')
        manage_addFolder(self.folder, 'folder11')
        manage_addFolder(self.folder, 'folder12')
        manage_addFolder(self.folder, 'folder13')
        self.db = DB(MappingStorage())
        self.connection = self.db.open()

    def tearDown(self):
        self.db.close()

    def test_basic(self):
        """ Let's create a folder with a few objects and change their order """
        order_seq = ['folder11', 'folder13', 'folder12']
        folderutils.sort_folder(self.folder, order_seq)
        self.assertEqual(self.folder.objectIds(), order_seq)

    def test_unchanged(self):
        """ Nothing changes """
        order_seq = self.folder.objectIds()
        folderutils.sort_folder(self.folder, order_seq)
        self.assertEqual(self.folder.objectIds(), order_seq)

    def test_incomplete(self):
        """ Some ids from the folder are missing in the call. This means that
        the folder must be reordered and the missing ids must be put at the
        end."""

        order_seq = ['folder13', 'folder12']
        folderutils.sort_folder(self.folder, order_seq)
        self.assertEqual(self.folder.objectIds(), order_seq + ['folder11'])

    def test_extra_id(self):
        """ An ID that is not inside the folder """

        order_seq = ['folder13', 'asdf']
        folderutils.sort_folder(self.folder, order_seq)
        self.assertEqual(self.folder.objectIds(),
                         ['folder13', 'folder11', 'folder12'])

    def test_no_unnecessary_commit(self):
        order_seq = self.folder.objectIds()
        folderutils.sort_folder(self.folder, order_seq)

        root = self.connection.root()
        root['folder'] = self.folder
        transaction.commit()

        order_seq.pop() # resulting order should be the same
        folderutils.sort_folder(self.folder, order_seq)
        # assert no commit to DB since no change was required by ordering
        self.assertEqual(self.connection._registered_objects, [])
