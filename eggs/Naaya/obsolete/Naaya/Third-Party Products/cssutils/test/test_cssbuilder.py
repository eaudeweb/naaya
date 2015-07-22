__version__ = '0.51'

import unittest
import xml.dom

from cssutils import *
from cssutils.cssbuilder import *


class CSSBuilderTestCase(unittest.TestCase):

    def test_init(self):
        css = StyleSheet()
        self.assertEqual([], css.getRules())

    def test_add_get(self):
        css = StyleSheet()
        r1 = StyleRule()
        r1.addSelector('.r1')
        c = Comment('x')
        css.addRule(r1)
        css.addRule(r1)
        css.addRule(c)
        self.assertEqual(3, len(css.getRules()))
        self.assertEqual(2, len(css.getRules(0))) # no comments

    def test_insert_delete(self):
        css = StyleSheet()
        r0 = '/* x */'
        r1 = '.r1 { color: red; }'
        r2 = '.r1 { color: red; }'

        # insert
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, '', 0)
        self.assertRaises(xml.dom.SyntaxErr, css.insertRule, '{}', 0)

        # insert 
        self.assertRaises(xml.dom.IndexSizeErr, css.insertRule, r1, 1)
        css.insertRule(r1, 0)
        css.insertRule(r2,0)
        css.insertRule(r1,0)

        self.assertEqual(3, len(css.getRules()))

        # delete        
        self.assertRaises(xml.dom.IndexSizeErr, css.deleteRule, 3)
        css.deleteRule(1)
        self.assertEqual(2, len(css.getRules()))

    def test_webexample(self):
        ## from cssutils.cssbuilder import *

        # init CSSStylesheet
        s = StyleSheet()

        # build a rule
        r = StyleRule()
        r.addSelector('body')
        r.addSelector('b') # a second one
        d = StyleDeclaration()
        d.setProperty('color', 'red') # former addProperty is DEPRECATED
        r.setStyleDeclaration(d)

        # build @media Rule
        mr = MediaRule(' print,   tv ')
        r2 = StyleRule('body')
        d2 = StyleDeclaration()
        d2.setProperty('color', '#000')
        r2.setStyleDeclaration(d2)
        mr.addRule(r2)

        # compose stylesheet
        s.addComment('basic styles')
        s.addComment('styles for print or tv')
        s.addRule(mr)
        s.insertRule(r, 1)
        # output
        ## s._pprint(2)
        expected = """/* basic styles */
body, b {
  color: red;
  }
/* styles for print or tv */
@media print, tv {
  body {
    color: #000;
    }
}"""
        actual = s._pprint(2)
        self.assertEqual(expected, actual)
        

if __name__ == '__main__':
    unittest.main() 