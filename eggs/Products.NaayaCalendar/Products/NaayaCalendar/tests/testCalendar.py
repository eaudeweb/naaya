
# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
from unittest import TestSuite, TestLoader
from DateTime import DateTime
from Products.Naaya.tests import NaayaTestCase

from Products.NaayaCalendar.EventCalendar import manage_addEventCalendar
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.event.event_item import addNyEvent

class Record:
    def __init__(self, **kw):
        self.__dict__.update(kw)

class NaayaCalendarTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaCalender object
    """
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Edit, Delete Naaya Calendar """

        calendar_id = 'portal_calendar'

        #add
        manage_addEventCalendar(self._portal(), id=calendar_id, title='Events calendar', day_len='3', start_day='Monday', catalog='portal_catalog')
        self.assertTrue(hasattr(self._portal(), calendar_id))

        #edit properties
        calendar = self._portal()._getOb(calendar_id)
        calendar.manageProperties(title='Events calendar edited', description='Calendar of events edited', day_len='1',
                         cal_meta_types='Naaya Event', start_day='Sunday', catalog='portal_catalog')

        self.assertEqual(calendar.getCalMetaTypes(), 'Naaya Event')
        self.assertEqual(calendar.catalog, 'portal_catalog')
        self.assertEqual(calendar.title, 'Events calendar edited')
        self.assertEqual(calendar.description, 'Calendar of events edited')
        self.assertEqual(calendar.day_len, '1')
        self.assertEqual(calendar.start_day, 'Sunday')

        #delete
        self._portal().manage_delObjects([calendar_id])
        self.assertFalse(hasattr(self._portal(), calendar_id))

    def test_events(self):
        """ Find NaayaEvents """

        calendar_id = 'portal_calendar'

        #add calendar
        manage_addEventCalendar(self._portal(), id=calendar_id, title='Events calendar', day_len='3', start_day='Monday', catalog='portal_catalog')
        calendar = self._portal()._getOb(calendar_id)
        calendar.cal_meta_types = calendar.setCalMetaTypes('Naaya Event')

        #add portal catalog index
        catalog = self._portal()._getOb('portal_catalog')
        extra = Record(since_field='start_date', until_field='end_date')
        catalog.addIndex('resource_interval', 'DateRangeIndex', extra)

        #add event
        addNyFolder(self._portal(), 'myfolder')
        addNyEvent(self._portal().myfolder, id='myevent', title='My event', lang='en', start_date="10/10/2000", end_date="15/10/2000")
        event = self._portal().myfolder._getOb('myevent')

        #get events
        self.assertEqual(calendar.getEvents(year=2000, month=10), [(event, '10 October 2000', '15 October 2000')])

    def _calendar_with_events(self):
        manage_addEventCalendar(self._portal(), id='portal_calendar', title='Events calendar', day_len='3', start_day='Monday', catalog='portal_catalog')
        calendar = self._portal()._getOb('portal_calendar')
        calendar.cal_meta_types = calendar.setCalMetaTypes('Naaya Event')
        catalog = self._portal()._getOb('portal_catalog')
        extra = Record(since_field='start_date', until_field='end_date')
        catalog.addIndex('resource_interval', 'DateRangeIndex', extra)
        addNyFolder(self._portal(), 'myfolder')
        folder = self._portal().myfolder
        addNyEvent(folder, id='e1', title='One', lang='en', start_date="10/10/2000", end_date="10/10/2000")
        addNyEvent(folder, id='e2', title='Two', lang='en', start_date="12/10/2000", end_date="13/10/2000")
        addNyEvent(folder, id='e3', title='Three', lang='en', start_date="13/10/2000", end_date="13/10/2000")
        addNyEvent(folder, id='e4', title='Four', lang='en', start_date="02/11/2000", end_date="02/11/2000")
        for ob_id in ['e1', 'e2', 'e3', 'e4']:
            folder[ob_id].approveThis()
            folder.recatalogNyObject(folder[ob_id])
        return calendar

    def test_events_by_day(self):
        calendar = self._calendar_with_events()
        days = calendar.hasEventsByDay(2000, 10)
        self.assertEqual(len(days), 31)
        self.assertEqual(days[10], '/myfolder/e1')
        self.assertEqual(days[12], '/myfolder/e2')
        self.assertEqual(days[13], True)
        self.assertEqual(days[11], False)
        self.assertEqual([e[0].getId() for e in calendar.getDayEvents(
            DateTime(2000, 10, 13))], ['e2', 'e3'])

    def test_events_by_month(self):
        calendar = self._calendar_with_events()
        months = calendar.getEventsByMonth()
        self.assertEqual(sorted(months), [(10, 2000), (11, 2000)])
        self.assertEqual([e[0].getId() for e in months[(10, 2000)]],
                         ['e1', 'e2', 'e3'])
        limited = calendar.getEventsByMonth(month_events_limit=1)
        self.assertEqual(len(limited[(10, 2000)]), 1)

    def test_show_calendar(self):
        calendar = self._calendar_with_events()
        request = calendar.REQUEST
        request.set('cyear', '2000')
        request.set('cmonth', '10')
        html = calendar.show_calendar()
        self.assertIn('October', html)
        self.assertIn('/myfolder/e1', html)
        self.assertIn('>13</a>', html)
        self.assertNotIn('>11</a>', html)

    def test_utRead(self):
        import os
        import tempfile
        calendar = manage_addEventCalendar(self._portal(), id='portal_calendar', title='', day_len='3', start_day='Monday', catalog='portal_catalog')
        calendar = self._portal()._getOb('portal_calendar')
        with tempfile.NamedTemporaryFile('wb', delete=False) as f:
            f.write('Căt'.encode('utf-8'))
        try:
            self.assertEqual(calendar.utRead(f.name), 'Căt')
            self.assertEqual(calendar.utRead(f.name, 'rb'),
                             'Căt'.encode('utf-8'))
        finally:
            os.unlink(f.name)


def test_suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(NaayaCalendarTestCase))
    return suite
