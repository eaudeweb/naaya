__version__ = '0.51'

import unittest
import xml.dom

from cssutils.cssimportrule import *
from cssutils.cssrule import CSSRule


class CSSImportRuleTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_emptyInit(self):
        i = ImportRule()
        self.assertEqual(CSSRule.IMPORT_RULE, i.type)
        self.assertEqual(u'', i.cssText)

    def test_emptyMediaList(self):
        i = ImportRule('', 'css/test.css')
        self.assertEqual(u'@import all url(css/test.css);', i.cssText)

        i.media.appendMedium('print')        
        self.assertEqual(u'@import print url(css/test.css);', i.cssText)

        i.media.appendMedium('tv')        
        self.assertEqual(u'@import print, tv url(css/test.css);', i.cssText)

    def test_fullInit(self):
        i = ImportRule('tv, print', 'css/test.css')
        self.assertEqual(u'@import tv, print url(css/test.css);', i.cssText)


if __name__ == '__main__':
    unittest.main() 