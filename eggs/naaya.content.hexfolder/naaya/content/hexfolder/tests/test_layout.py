import unittest


class LayoutCheckTest(unittest.TestCase):

    def test_unknown_layout(self):
        from naaya.content.hexfolder.hexfolder_item import NyHexfolder
        errors = {}
        NyHexfolder._check_picture_info(None, {'layout_type': 'hexfolder_index'}, errors)
        self.assertEqual(errors, {'layout_type': ['Unknown layout']})

    def test_known_layout_checks_fields(self):
        from naaya.content.hexfolder.hexfolder_item import NyHexfolder
        errors = {}
        NyHexfolder._check_picture_info(
            None, {'layout_type': 'hexfolder_index_4', 'picture_0_long_description': 'x',
                   'picture_0': 'data'}, errors)
        self.assertEqual(errors, {})
