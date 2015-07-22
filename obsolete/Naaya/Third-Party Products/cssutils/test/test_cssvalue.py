__version__ = '0.41'

import unittest
import xml.dom

from cssutils.cssvalue import *


class CSSValueTestCase(unittest.TestCase):

    def test_init(self):
        v = Value('1')
        self.assertEqual('1', v.cssText)
        self.assertEqual(Value.CSS_CUSTOM, v.cssValueType) # dummy!

        v = Value('   1   px  ')
        self.assertEqual('1 px', v.cssText)
        self.assertEqual(Value.CSS_CUSTOM, v.cssValueType) # dummy!
    
        
if __name__ == '__main__':
    unittest.main() 