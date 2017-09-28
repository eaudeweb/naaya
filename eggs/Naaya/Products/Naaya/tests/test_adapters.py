from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.adapters import FolderMetaTypes
from Products.Naaya.NyFolder import addNyFolder


class TestFolderMetaTypesAdapter(NaayaTestCase):


    def subfolders_unchanged(self):
        """ Helper method, tests that subfolder metatypes are unchanged """
        for w in self.wrapped[1:]:
            self.assertEqual(set(self.defaults), set(w.get_values()))
            self.assertFalse(w.has_custom_value)

    def setUp(self):
        super(TestFolderMetaTypesAdapter, self).setUp()
        addNyFolder(self.portal.info, 'subfolder0', contributor='contributor',
                    submission=1)
        addNyFolder(self.portal.info, 'subfolder1', contributor='contributor',
                    submission=1)
        self.wrapped = [FolderMetaTypes(x) for x in
                        [self.portal.info,
                         self.portal.info.subfolder0,
                         self.portal.info.subfolder1]]
        self.defaults = self.portal.adt_meta_types

    def test_defaults_loaded(self):
        for w in self.wrapped:
            self.assertEqual(set(self.defaults), set(w.get_values()))
            self.assertFalse(w.has_custom_value)

    def test_defaults_work(self):
        portal_properties = self.portal.getPropertiesTool()
        portal_properties.manageSubobjects([], ['Naaya Calendar'])
        for w in self.wrapped:
            self.assertEqual(['Naaya Calendar'], w.get_values())

    def test_add(self):
        self.wrapped[0].add('Test Type')
        self.assertEqual(set(self.defaults + ['Test Type']),
                         set(self.wrapped[0].get_values()))
        self.assertTrue(self.wrapped[0].has_custom_value)
        self.subfolders_unchanged()

    def test_remove(self):
        self.wrapped[0].remove(self.defaults[0])
        self.assertEqual(set(self.defaults[1:]),
                         set(self.wrapped[0].get_values()))
        self.assertTrue(self.wrapped[0].has_custom_value)
        self.subfolders_unchanged()

    def test_set(self):
        self.wrapped[0].set_values(['Test 1', 'Test 2'])
        self.assertEqual(set(['Test 1', 'Test 2']),
                         set(self.wrapped[0].get_values()))
        self.assertTrue(self.wrapped[0].has_custom_value)
        self.subfolders_unchanged()

    def test_set_default(self):
        self.wrapped[0].set_values(['Test 1', 'Test 2'])
        self.wrapped[0].set_values(None)
        self.assertFalse(self.wrapped[0].has_custom_value)
        self.assertEqual(set(self.defaults), set(self.wrapped[0].get_values()))
        self.subfolders_unchanged()
