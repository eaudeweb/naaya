__version__ = '0.51'

import unittest
import xml.dom

from cssutils.cssfontfacerule import *
from cssutils.cssbuilder import CSSRule, StyleDeclaration


class CSSFontFaceRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.s = StyleDeclaration()
        self.s.setProperty('color', 'red')

    def test_emptyInit(self):
        f = FontFaceRule()
        self.assertEqual(cssrule.CSSRule.FONT_FACE_RULE, f.type)
        self.assertEqual(u'', f.cssText)

    def test_fullInit(self):
        f = FontFaceRule(self.s)
        self.assertEqual(u'@font-face {\n    color: red;\n    }', f.cssText)

    def test_readonly(self):
        pass


if __name__ == '__main__':
    unittest.main() 