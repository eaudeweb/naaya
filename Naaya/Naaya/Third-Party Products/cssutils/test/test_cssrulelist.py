__version__ = '0.41'

import unittest

from cssutils.cssrulelist import *


class CSSRuleListTestCase(unittest.TestCase):

    def test_(self):
        r = RuleList()
        self.assertEqual(0, r.length)
        self.assertEqual(None, r.item(2))

        # subclasses list!
        r.append(0)
        r.append(1)
        self.assertEqual(2, r.length)
        self.assertEqual(1, r.item(1))
        self.assertEqual(None, r.item(2))


if __name__ == '__main__':
    unittest.main() 