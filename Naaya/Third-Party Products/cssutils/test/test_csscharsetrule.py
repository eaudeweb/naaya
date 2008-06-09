__version__ = '0.51'

import unittest
import xml.dom

from cssutils.csscharsetrule import *
from cssutils.cssrule import CSSRule


class CSSCharsetRuleTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_emptyInit(self):
        c = CharsetRule()
        self.assertEqual(CSSRule.CHARSET_RULE, c.type)
        self.assertEqual(u'', c.cssText)

        c.encoding = 'UTF-8'
        self.assertEqual(u'@charset "UTF-8";', c.cssText)

    def test_readonly(self):
        c = CharsetRule(encoding='iso-8859-1', readonly=True)
        self.assertEqual(u'@charset "iso-8859-1";', c.cssText)      
        self.assertRaises(xml.dom.NoModificationAllowedErr, c._setEncoding, 'utf-8')
        self.assertEqual(u'@charset "iso-8859-1";', c.cssText)      

    def test_encodings(self):
        c = CharsetRule('utf-8')
        self.assertEqual(u'@charset "utf-8";', c.cssText)      

        c.encoding = 'iso-8859-1'
        self.assertEqual(u'@charset "iso-8859-1";', c.cssText)      


if __name__ == '__main__':
    unittest.main() 