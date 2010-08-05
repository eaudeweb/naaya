__version__ = '0.41'

import unittest
import xml.dom
from cssutils.cssproperties import *


class PropertyTestCase(unittest.TestCase):

    def test_init(self):

        self.assertRaises(xml.dom.SyntaxErr, Property, 'invalid name', 'some value')

        p = Property('color', 'red')
        self.assertEqual('color: red;', p.cssText)

        p = Property('  color   ', '  red  ', 'important')
        self.assertEqual('color: red !important;', p.cssText)

        self.assertEqual('color', p.getName())
        self.assertEqual('red', p.getValue())
        self.assertEqual('important', p.getPriority())

if __name__ == '__main__':
    unittest.main() 