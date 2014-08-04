import unittest
from naaya.core.zope2util import simple_paginate

class PaginatorTest(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(simple_paginate([], 4), [])

    def test_10_items(self):
        self.assertEqual(simple_paginate(range(10), 4),
                         [[0,1,2,3], [4,5,6,7], [8,9]])

    def test_1_item(self):
        self.assertEqual(simple_paginate([1], 4), [[1]])

    def test_3_item(self):
        self.assertEqual(simple_paginate(range(3), 4), [[0,1,2]])

    def test_4_item(self):
        self.assertEqual(simple_paginate(range(4), 4), [[0,1,2,3]])

    def test_5_item(self):
        self.assertEqual(simple_paginate(range(5), 4), [[0,1,2,3], [4]])
