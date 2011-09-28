import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.RDFCalendar.RDFCalendar import RDFCalendar

class RDFCalendarTestCase(ZopeTestCase.ZopeTestCase):

    _setup_fixture = 0

    def testCreationWithDefaults(self):
	c = RDFCalendar('mycal')
	self.assertEquals(6, c.first_day_week)

    def testMonday(self):
	c = RDFCalendar('mycal', '', 'Monday', 3)
        self.assertEquals(0, c.first_day_week)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RDFCalendarTestCase))
    return suite

if __name__ == '__main__':
    framework()
