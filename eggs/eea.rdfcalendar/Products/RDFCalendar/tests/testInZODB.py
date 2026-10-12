import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('RDFCalendar')

class RDFCalendarInZopeTestCase(ZopeTestCase.ZopeTestCase):

    def testAddCalendar(self):
        self.app.manage_addProduct['RDFCalendar'].manage_addRDFCalendar('mycal', 'Title')
        self.assertTrue(hasattr(self.app, 'mycal'),'Calendar did not get created')
        self.assertNotEqual(self.app.mycal, None)

    def test_show_month(self):
        now_month = time.localtime().tm_mon
        self.app.manage_addProduct['RDFCalendar'].manage_addRDFCalendar('mycal', 'Title')
	self.assertEquals(now_month, self.app.mycal.getMonth())
	self.app.REQUEST.set('month', '12')
	self.assertEquals(12, self.app.mycal.getMonth())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RDFCalendarInZopeTestCase))
    return suite

if __name__ == '__main__':
    framework()
