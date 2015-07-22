__version__ = '0.41'

import unittest
import xml.dom

import cssutils.cssrule
from cssutils.cssmediarule import *


class CSSMediaRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.r = MediaRule()

    def test_init(self):
        self.assertEqual(cssutils.cssrule.CSSRule.MEDIA_RULE, self.r.type)
        self.assertEqual(u'@media all {\n}', self.r.cssText)

    def test_media(self):
        pass

if __name__ == '__main__':
    unittest.main() 