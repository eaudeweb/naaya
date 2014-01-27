import unittest
from datetime import datetime

from naaya.core.custom_types import Interval

class IntervalTestCase(unittest.TestCase):
    """ TestCase for Interval data type """

    def test_create_blank(self):
        i = Interval()
        self.assertTrue(i.start_date is None)
        self.assertTrue(i.end_date is None)
        self.assertTrue(isinstance(i.all_day, bool))
        self.assertTrue(i.all_day is False)

    def test_create(self):
        start_date = datetime(2011, 3, 23, 10, 0)
        end_date = datetime(2011, 3, 24, 19, 30)
        i = Interval(start_date, end_date, False)
        self.assertTrue(isinstance(i.start_date, datetime))
        self.assertTrue(isinstance(i.end_date, datetime))
        self.assertTrue(isinstance(i.all_day, bool))
        self.assertEqual(i.start_date, start_date)
        self.assertEqual(i.end_date, end_date)
        self.assertEqual(i.all_day, False)

    def test_create_all_day(self):
        # hour:minutes must anyway be ignored
        start_date = datetime(2011, 3, 23, 10, 0)
        end_date = datetime(2011, 3, 24, 19, 30)
        i = Interval(start_date, end_date, True)
        self.assertEqual(i.start_date, datetime(2011, 3, 23))
        self.assertEqual(i.end_date, datetime(2011, 3, 24))
        self.assertEqual(i.all_day, True)

    def test_repr(self):
        start_date = datetime(2011, 3, 22, 10, 0)
        end_date = datetime(2011, 3, 24, 10, 30)
        i = Interval(start_date, end_date, False)
        self.assertEqual(repr(i), ("Interval:[22/03/2011, 10:00 - "
                                   "24/03/2011, 10:30; All day: False]"))

