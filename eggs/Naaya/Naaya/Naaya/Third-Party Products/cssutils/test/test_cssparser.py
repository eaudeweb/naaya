__version__ = '0.51'

import unittest
import xml.dom

from cssutils.cssparser import CSSParser


class CSSParserTestCase(unittest.TestCase):

    def setUp(self):
        self.p = CSSParser()

    def test_rules(self):
        cssText = """
            /* comment */
            a { color: red;}            
            """        
        self.p.parseString(cssText)

    def test_charsetrule(self):      
        actual = self.p.parseString('  @charset   ; ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @charset; ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @charset {} ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @charset  "ISO-8859-1"  ; ')._pprint()
        self.assertEqual(u'@charset "ISO-8859-1";', actual)
        actual = self.p.parseString('@charset"ISO-8859-1";')._pprint()
        self.assertEqual(u'@charset "ISO-8859-1";', actual)
        actual = self.p.parseString('@charset"ISO-8859-1";')._pprint()
        self.assertEqual(u'@charset "ISO-8859-1";', actual)

    def test_fontfacerule(self):      
        actual = self.p.parseString('  @font-face   {   }   ; ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @font-face     ; ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @font-face  {} ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @font-face   {  font-family: serif } ; ')._pprint()
        self.assertEqual(u'@font-face {\n    font-family: serif;\n    }', actual)
        actual = self.p.parseString('@font-face{font-family:serif};')._pprint()
        self.assertEqual(u'@font-face {\n    font-family: serif;\n    }', actual)

    def test_importrule(self):      
        actual = self.p.parseString('  @import url( css/test.css   ); ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @import screenurl( css/test.css   ); ')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('@importscreen,tv,print url(css/test.css);')._pprint()
        self.assertEqual(u'', actual)
        actual = self.p.parseString('  @import  screen,tv  ,  print  url( css/test.css ) ; ')._pprint()
        self.assertEqual(u'@import screen, tv, print url(css/test.css);', actual)
        actual = self.p.parseString('@import screen,tv,print url(css/test.css);')._pprint()
        self.assertEqual(u'@import screen, tv, print url(css/test.css);', actual)


if __name__ == '__main__':
    unittest.main() 