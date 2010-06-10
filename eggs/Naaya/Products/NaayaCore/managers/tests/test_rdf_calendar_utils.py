# -*- coding: utf-8 -*-
from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from naaya.content.event.event_item import config, addNyEvent

class TestCase(NaayaFunctionalTestCase):

    def afterSetUp(self):
        addNyEvent(self.portal.info, id='event1', title='event1',
                   start_date='12/12/2010', end_date='13/12/2010', lang='en')
        addNyEvent(self.portal.info, id='event1_fr', title='event1_fr',
                   start_date='12/12/2010', end_date='12/12/2010', lang='fr')

    def test_rdf_cataloged_items(self):
        items = self.portal.rdf_cataloged_items(config['meta_type'])
        self.assertEqual(len(items), 2)
        #self.assertEqual(items[0]['title'], u'event1')

        #Overriding field
        items = self.portal.rdf_cataloged_items(config['meta_type'], {
            'startdate': 'releasedate',
        })
        self.assertEqual(items[0]['startdate'], items[0]['updated'])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestCase))
    return suite
