__version__ = '0.51'

import exceptions
import unittest

from cssutils.cssrule import *


class CSSRuleTestCase(unittest.TestCase):

    def test_init(self):
        r = CSSRule()
        self.assertEqual(CSSRule.UNKNOWN_RULE, r.type)
        

class SimpleAtRuleTestCase(unittest.TestCase):

    def test_init(self):
        self.assertRaises(exceptions.DeprecationWarning, SimpleAtRule)


if __name__ == '__main__':
    unittest.main() 