__version__ = '0.41'

import unittest
import xml.dom

import cssutils.cssrule
import cssutils.cssstyledeclaration
from cssutils.cssstylerule import *


class CSSStyleRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.r = StyleRule()
        self.d = cssutils.cssstyledeclaration.StyleDeclaration()

    def test_init(self):
        self.assertEqual(cssutils.cssrule.CSSRule.STYLE_RULE, self.r.type)

    def test_selectors(self):
        self.assertEqual(0, len(self.r.getSelectors()))
        self.r.addSelector(u'a')
        self.assertEqual(1, len(self.r.getSelectors()))     
        self.assertEqual(u'a', self.r.selectorText)
        self.r.addSelector(u' b  , h1 ')
        self.assertEqual(3, len(self.r.getSelectors()))
        self.assertEqual(u'a, b, h1', self.r.selectorText)
        # comments

    def test_get_set_style(self):
        self.r.setStyleDeclaration(self.d)
        self.assertEqual(self.d, self.r.getStyleDeclaration())
        self.r.style = self.d

    def test_getFormatted(self):
        self.r.addSelector(' b  , h1 ')
        self.r.setStyleDeclaration(self.d)
        self.assertEqual(u'b, h1 {\n\n}', self.r.getFormatted(0,0))    
        self.assertEqual(u'b, h1 {\n\n    }', self.r.cssText)    


if __name__ == '__main__':
    unittest.main() 