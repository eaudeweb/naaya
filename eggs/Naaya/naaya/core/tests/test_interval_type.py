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
        i = Interval('23/03/2011', '10:00', '24/03/2011', '19:30', False)
        self.assertTrue(isinstance(i.start_date, datetime))
        self.assertTrue(isinstance(i.end_date, datetime))
        self.assertTrue(isinstance(i.all_day, bool))
        self.assertEqual(i.start_date, datetime(2011, 3, 23, 10, 0))
        self.assertEqual(i.end_date, datetime(2011, 3, 24, 19, 30))
        self.assertEqual(i.all_day, False)

    def test_create_all_day(self):
        # hour:minutes must anyway be ignored
        i = Interval('23/03/2011', '8:00', '24/03/2011', '19:30', True)
        self.assertEqual(i.start_date, datetime(2011, 3, 23))
        self.assertEqual(i.end_date, datetime(2011, 3, 24))
        self.assertEqual(i.all_day, True)

    def test_create_error(self):
        # invalid date (format)
        self.assertRaises(ValueError,
             lambda: Interval('23//2011', '10:00', '24/03/2011', '19:30', True))
        # invalid hour
        self.assertRaises(ValueError,
           lambda: Interval('23/03/2011', 'a:00', '24/03/2011', '29:30', False))
        # invalid date (month)
        self.assertRaises(ValueError,
           lambda: Interval('03/23/2011', '10:00', '24/03/2011', '19:30', True))
        # end time precedes start time
        self.assertRaises(ValueError,
           lambda: Interval('24/03/2011', '10:00', '24/03/2011', '9:30', False))
        # shouldn't raise error, all day is True, hours ignored
        Interval('24/03/2011', '10:00', '24/03/2011', '9:30', True)
        # unspecified hours when all_day is False
        self.assertRaises(ValueError,
              lambda: Interval('23/03/2011', '', '24/03/2011', '', False))

    def test_repr(self):
        i = Interval('22/03/2011', '10:00', '24/03/2011', '10:30', False)
        self.assertEqual(repr(i), ("Interval:[22/03/2011, 10:00 - "
                                   "24/03/2011, 10:30; All day: False]"))

