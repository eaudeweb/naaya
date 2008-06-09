__version__ = '0.51'

import unittest
import xml.dom

from cssutils.csspagerule import *
from cssutils.cssbuilder import CSSRule, StyleDeclaration


class CSSPageRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.s = StyleDeclaration()
        self.s.setProperty('color', 'red')

    def test_emptyInit(self):
        p = PageRule()
        self.assertEqual(cssrule.CSSRule.PAGE_RULE, p.type)
        self.assertEqual(u'', p.cssText)

    def test_noSelector(self):
        p = PageRule()
        p.style = self.s
        self.assertEqual(u'@page {\n    color: red;\n    }', p.cssText)

    def test_fullInit(self):
        p = PageRule(':left', self.s)
        self.assertEqual(u'@page :left {\n    color: red;\n    }', p.cssText)

    def test_fullSet(self):
        p = PageRule()
        p.selectorText = ' :first,:left      ,   :right '
        p.style = self.s
        self.assertEqual(u'@page :first, :left, :right {\n    color: red;\n    }', p.cssText)

    def test_readonly(self):
        p = PageRule(':left', self.s, readonly=True)
        self.assertRaises(xml.dom.NoModificationAllowedErr, p._setSelectorText, u':left')
        p = PageRule(':left', self.s, readonly=True)
        self.assertRaises(xml.dom.NoModificationAllowedErr, p._setStyle, self.s)


if __name__ == '__main__':
    unittest.main() 