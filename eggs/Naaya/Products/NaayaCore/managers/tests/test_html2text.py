import unittest
from Products.NaayaCore.managers.utils import html2text

class Html2TextTest(unittest.TestCase):
    def test_blank(self):
        self.assertEqual(html2text(""), "")

    def test_strip_tags(self):
        self.assertEqual(html2text('<input type="text">'), "")
        self.assertEqual(html2text('<script>alert(1)</script>'), "alert(1)")

    def test_trim(self):
        self.assertEqual(html2text("<b>hello</b> world!", trim_length=4),
                         "hell")
        self.assertEqual(html2text("blah blah some text", trim_length=4),
                         "blah")

    def test_strip_whitespace(self):
        self.assertEqual(html2text(' something   '), 'something')

    def test_ellipsis(self):
        self.assertEqual(html2text("some long text here", trim_length=12),
                         "some long te")
        self.assertEqual(html2text("some long text here",
                                   trim_length=12, ellipsis=True),
                         u"some long \u2026")

    def test_long_trim(self):
        self.assertEqual(html2text('short text',
                                   trim_length=100, ellipsis=True),
                         'short text')
