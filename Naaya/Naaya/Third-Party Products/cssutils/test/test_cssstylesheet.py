__version__ = '0.41'

import unittest
import xml.dom

import cssutils.cssstyledeclaration
from cssutils import *
from cssutils.cssstylesheet import *
from cssutils.cssstylerule import *

class CSSStyleSheetTestCase(unittest.TestCase):

    def setUp(self):
        self.r1s = '.r1 {\n    color: red;\n    }' # rule string

        self.r1 = StyleRule() # Rule object
        self.r1.selectorText = '.r1'
        d = cssutils.cssstyledeclaration.StyleDeclaration()
        d.addProperty('color', 'red')
        self.r1.setStyleDeclaration(d)
    
    def test_init(self):
        css = StyleSheet()
        self.assertEqual(False, css._readonly)
        self.assertEqual([], css.getRules())

    def test_readonly(self):
        css = StyleSheet(True)
        self.assertEqual(True, css._readonly) # internal...
        self.assertRaises(xml.dom.NoModificationAllowedErr, css.addRule, self.r1)
        self.assertRaises(xml.dom.NoModificationAllowedErr, css.insertRule, self.r1s, 0)
        self.assertRaises(xml.dom.NoModificationAllowedErr, css.deleteRule, 0)

    def test_add_get(self):
        css = StyleSheet()
        c = Comment('x')
        css.addRule(self.r1)
        css.addRule(self.r1)
        css.addRule(c)
        css.addRule(self.r1)
        
        self.assertEqual(4, len(css.getRules())) # with comment
        self.assertEqual(3, len(css.getRules(False))) # without comment

        self.assertEqual(css.cssRules, css.getRules(False))

    def test_add_insert(self):
        css1 = StyleSheet()
        css2 = StyleSheet()

        css1.addRule(self.r1)
        css1.insertRule(self.r1s, 0)
        css2.insertRule(self.r1, 0)

        self.assertEqual(self.r1.cssText, self.r1s)        

        r1 = css1.getRules().item(0)        
        r2 = css2.getRules().item(0)

        self.assertEqual(r1.cssText, r2.cssText)        

    def test_insert(self):
        css = StyleSheet()

        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, u'', 0)
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, u' { }', 0)
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, u' { color: red;', 0)
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, u'{ color: blue;}', 0)
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, u'a { color: red;', 0)
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, u'a { color red; }', 0)

        self.assertEqual(0, css.insertRule(u'a { color: red; }', 0))

        self.assertRaises(xml.dom.IndexSizeErr, css.insertRule, self.r1s, 2)

        self.assertEqual(0, css.insertRule(self.r1s, -1))
        self.assertEqual(0, css.insertRule(self.r1s, 0))
        self.assertEqual(2, css.insertRule(self.r1s, 2))
        self.assertEqual(4, len(css.getRules()))

        # position ok?
        css.insertRule('.r2 { color: red; }', 1)
        self.assertEqual('.r2', css.getRules()[1].cssText[:3])        

    def test_insertImport(self):
        css = StyleSheet()
        css.insertRule('.r2 { color: red; }', 0)
        self.assertRaises(xml.dom.HierarchyRequestErr, css.insertRule, '@import all url(test.css);', 1)
        self.assertEqual(1, len(css.getRules()))
        css.insertRule('@import all url(test.css);', 0)
        self.assertEqual(2, len(css.getRules()))

        css = StyleSheet()
        css.addComment('test')
        css.insertRule('@import all url(test.css);', 0)
        css.insertRule('@import print url(test.css);', 1)
        self.assertEqual(3, len(css.getRules()))


    def test_delete(self):
        css = StyleSheet()

        css.insertRule(self.r1s, 0)
        css.insertRule(self.r1s, 0)
        css.insertRule(self.r1s, 0)
        css.insertRule(u'.r2 { color: red; }', 1)
        self.assertEqual(4, len(css.getRules()))

        self.assertRaises(xml.dom.IndexSizeErr, css.deleteRule, 4)

        # deleted the right one?
        self.assertEqual(u'.r2', css.getRules()[1].cssText[:3])        
        css.deleteRule(1)
        self.assertEqual(3, len(css.getRules()))
        self.assertEqual(u'.r1', css.getRules()[1].cssText[:3])        

    def test_insertorder(self):
        css = StyleSheet()

        r0s = u'/* x */'
        r2s = u'.r1 { color: red; }'

        css.insertRule(self.r1s, 0)
        css.insertRule(r2s,0)
        css.insertRule(self.r1s,0)
        

if __name__ == '__main__':
    unittest.main()
