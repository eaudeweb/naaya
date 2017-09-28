from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.adapters import FolderMetaTypes


class TestFolderSubobjects(NaayaTestCase):

    def setUp(self):
        super(TestFolderSubobjects, self).setUp()
        self.portal_properties = self.portal.getPropertiesTool()

    def test_setting_default_subobjects(self):
        self.portal_properties.manageSubobjects(['ZopeType0', 'ZopeType1'],
                                                ['NyType0', 'NyType1'])
        fmt = FolderMetaTypes(self.portal.info)
        self.assertEqual(set(fmt.get_values()),
                         set(['ZopeType0', 'ZopeType1', 'NyType0', 'NyType1']))
        self.assertEqual(set(fmt.get_values()), set(self.portal.adt_meta_types))

    def test_update_only_nysubobjects(self):
        self.portal_properties.manageSubobjects(['ZopeType0', 'ZopeType1'],
                                                self.portal.get_meta_types(1))
        self.portal_properties.manageSubobjects([], ['Naaya Document'],
                                                only_nyobjects=True)
        self.assertEqual(set(self.portal.adt_meta_types),
                         set(['ZopeType0', 'ZopeType1', 'Naaya Document']))
