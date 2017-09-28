
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
from unittest import TestSuite, makeSuite
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


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaCalendarTestCase))
    return suite
