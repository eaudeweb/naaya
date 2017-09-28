from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from naaya.content.event.event_item import config, addNyEvent
from Products.NaayaCore.managers.rdf_calendar_utils import date_format

class TestCase(NaayaFunctionalTestCase):

    def afterSetUp(self):
        addNyEvent(self.portal.info, id='event1', title='event1',
                   start_date='12/12/2010', end_date='13/12/2010', lang='en')
        addNyEvent(self.portal.info, id='event1_fr', title='event1_fr',
                   start_date='12/12/2010', end_date='12/12/2010', lang='fr')
        addNyEvent(self.portal.info, id='event2', title='event2',
                   start_date='28/11/2010', end_date='02/12/2010', lang='fr')

    def test_rdf_cataloged_items(self):
        items = self.portal.rdf_cataloged_items(config['meta_type'],
                                                year=2010, month=12)
        self.assertEqual(len(items), 3)

        #Overriding field
        items = self.portal.rdf_cataloged_items(config['meta_type'], {
            'startdate': 'releasedate',
        }, year=2010, month=12)
        item = {}
        for item_dict in items:
            if item_dict['id'] == 'event1':
                item = item_dict
                break
        self.assertEqual(item['startdate'],
                    self.portal.info.event1.releasedate.strftime(date_format))
