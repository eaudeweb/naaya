__version__ = '0.41'

import unittest
import xml.dom

from cssutils.cssstyledeclaration import *


class CSSDeclarationTestCase(unittest.TestCase):

    def setUp(self):
        self.s = StyleDeclaration()
        
    def test_init(self):
        self.assertEqual(0, self.s.length)

    def test_set(self):
        self.assertEqual(0, self.s.length)
        self.s.setProperty(u'color', u'red')
        self.s.setProperty(u'left', u'5px', u'important')
        self.assertEqual(2, self.s.length)

        # TODO

        #self.s.addComment('test')
        #self.assertEqual(3, self.s.length)

        #   exception

    def test_cssText(self):
        self.assertEqual(u'', self.s.cssText)
        self.test_set()
        self.assertEqual(u'    color: red;\n    left: 5px !important;', self.s.cssText)

    def test_get(self):
        self.test_set()
        # cssutils -> object
        self.assertEqual(None, self.s.getProperty(u''))
        self.assertEqual(None, self.s.getProperty(u'test'))
        self.assertEqual(u'red', self.s.getProperty(u'color').getValue() )
        self.assertEqual(u'left', self.s.getProperty(u'left').getName())

        # dom -> string
        self.assertEqual(u'', self.s.getPropertyValue(u''))
        self.assertEqual(u'', self.s.getPropertyValue(u'test'))
        self.assertEqual(u'red', self.s.getPropertyValue(u'color'))
        self.assertEqual(u'5px', self.s.getPropertyValue(u'left'))

        self.assertEqual(None, self.s.getPropertyCSSValue(u'test'))
        self.assertEqual(u'red', self.s.getPropertyCSSValue(u'color').cssText)
        self.assertEqual(u'5px', self.s.getPropertyCSSValue(u'left').cssText)
        # test shorthand property

        self.assertEqual(u'', self.s.getPropertyPriority(u'color'))
        self.assertEqual(u'important', self.s.getPropertyPriority(u'left'))
        self.assertEqual(u'', self.s.getPropertyPriority(u'test'))
        self.assertEqual(u'', self.s.getPropertyPriority(u''))

    def test_item(self):
        self.test_set()
        self.assertEqual(u'color', self.s.item(0))
        self.assertEqual(u'left', self.s.item(1))
        self.assertEqual(u'', self.s.item(2))
        
    def test_remove(self):
        self.test_set()
        self.assertEqual(u'', self.s.removeProperty(''))
        self.assertEqual(2, self.s.length)
        self.assertEqual(u'red', self.s.removeProperty(u'color'))
        self.assertEqual(1, self.s.length)
        self.assertEqual(u'5px', self.s.removeProperty(u'left'))
        self.assertEqual(0, self.s.length)
        self.assertEqual(u'', self.s.removeProperty(u'test'))
        self.assertEqual(0, self.s.length)


if __name__ == '__main__':
    unittest.main() 