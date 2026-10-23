import os
import time

from Testing import ZopeTestCase
ZopeTestCase.installProduct('RDFCalendar')
ZopeTestCase.installProduct('RDFSummary')

FEED = 'file://' + os.path.join(os.path.dirname(__file__), 'events.rdf')


class RDFCalendarInZopeTestCase(ZopeTestCase.ZopeTestCase):

    def add_calendar(self):
        self.app.manage_addProduct['RDFCalendar'].manage_addRDFCalendar(
            'mycal', 'Title')
        cal = self.app.mycal
        cal.manage_addProduct['RDFSummary'].manage_addRDFSummary(
            'events', 'Events', FEED, '', 'no', self.app.REQUEST)
        cal.manage_updateChannels()
        return cal

    def testAddCalendar(self):
        self.app.manage_addProduct['RDFCalendar'].manage_addRDFCalendar('mycal', 'Title')
        self.assertEqual(self.app.mycal.meta_type, 'RDF Calendar')
        self.assertEqual(self.app.mycal.title, 'Title')

    def test_show_month(self):
        now_month = time.localtime().tm_mon
        self.app.manage_addProduct['RDFCalendar'].manage_addRDFCalendar('mycal', 'Title')
        self.assertEqual(now_month, self.app.mycal.getMonth())
        self.app.REQUEST.set('month', '12')
        self.assertEqual(12, self.app.mycal.getMonth())

    def test_channel_events(self):
        cal = self.add_calendar()
        events = cal.get_events(2030, 3)
        self.assertEqual([e['title'] for e in events], ['Green fair'])
        self.assertEqual(events[0]['location'], 'Brașov')
        self.assertEqual([e['title'] for e in cal.get_events(2030, 3, 11)],
                         ['Green fair'])
        self.assertEqual(cal.get_events(2030, 3, 13), [])
        self.assertEqual([e['title'] for e in cal.get_events(2030, 4)],
                         ['Expo'])
        self.assertEqual(cal.get_events(2030, 5), [])
