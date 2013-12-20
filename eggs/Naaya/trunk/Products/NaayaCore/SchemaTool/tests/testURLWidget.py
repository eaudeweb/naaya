import unittest

from Products.NaayaCore.SchemaTool.widgets.URLWidget import convert_string_to_URL

class StringToURLConversion(unittest.TestCase):

    def test_relative_url(self):
        self.assertEqual(convert_string_to_URL('/example/index_html'),
                         '/example/index_html')

        self.assertEqual(convert_string_to_URL('example/index_html'),
                         'example/index_html')

        self.assertEqual(convert_string_to_URL('./example/index_html'),
                         './example/index_html')

    def test_no_schema(self):
        self.assertEqual(convert_string_to_URL('www.example.com'),
                         'http://www.example.com')

    def test_absolute_url(self):
        self.assertEqual(convert_string_to_URL('http://www.example.com'),
                         'http://www.example.com')

        self.assertEqual(convert_string_to_URL('https://www.example.com'),
                         'https://www.example.com')

        self.assertEqual(convert_string_to_URL('ftp://www.example.com'),
                         'ftp://www.example.com')

