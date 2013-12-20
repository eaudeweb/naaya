# encoding: utf-8
import unittest
from lxml.html.soupparser import fromstring
import re
from datetime import datetime

from Products.NaayaCore.SchemaTool.Schema import Schema
from Products.NaayaCore.SchemaTool.widgets.IntervalWidget import (
    Interval, IntervalWidget, addIntervalWidget, WidgetError)
from Products.Naaya.tests import NaayaTestCase


class IntervalWidgetTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Interval widget """

    def afterSetUp(self):
        widget = IntervalWidget('interval-property', title='Interval', lang='en')
        self.widget = widget.__of__(self.portal.portal_schemas.NyDocument)

    def test_edit_form(self):
        start_date = datetime(2011, 3, 25, 8, 0)
        end_date = datetime(2011, 3, 26, 8, 30)
        html = self.widget.render_html(Interval(start_date, end_date, False))
        dom = fromstring(re.sub('\s+', ' ', html))
        val = lambda xp: dom.xpath(xp)[0].attrib['value']
        self.assertEqual('08:30', val('//input[@name="interval.end_time"]'))
        self.assertEqual('25/03/2011',
                         val('//input[@name="interval.start_date"]'))
        checkbox = '//input[@name="interval.all_day:boolean"]'
        self.assertFalse(dom.xpath(checkbox)[0].attrib.has_key('checked'))

    def test_parse_data(self):
        output = self.widget.parseFormData({'start_date': '30/11/2010',
                                            'start_time': '8:00',
                                            'end_date': '01/12/2010',
                                            'end_time': '20:00'})
        self.assertTrue(isinstance(output, Interval))
        start_date = datetime(2010, 11, 30, 8, 0)
        end_date = datetime(2010, 12, 1, 20, 0)
        self.assertEqual(output, Interval(start_date, end_date, False))
        self.assertEqual(self.widget.parseFormData(''), None)

    def test_parse_bad_data(self):
        try:
            self.widget.parseFormData({'start_date': '30/11/2010',
                                       'start_time': '8:00',
                                       'end_date': '01/12/2010',
                                       'end_time': '0a:00'})
            self.fail('should raise exception')
        except WidgetError, e:
            self.assertTrue("Bad value ('01/12/2010', '0a:00') for End Time"
                            in str(e))

        bad_inputs = [# invalid date (format)
                      ('23//2011', '10:00', '24/03/2011', '19:30', 'on'),
                      # invalid hour
                      ('23/03/2011', 'a:00', '24/03/2011', '29:30', ''),
                       # invalid date (month)
                      ('03/23/2011', '10:00', '24/03/2011', '19:30', 'on'),
                      # end time precedes start time
                      ('24/03/2011', '10:00', '24/03/2011', '9:30', ''),
                      # unspecified hours when all_day is False
                      ('23/03/2011', '', '24/03/2011', '', '')]
        for bi in bad_inputs:
            self.assertRaises(WidgetError, self.widget.parseFormData,
                              {'start_date': bi[0],
                               'start_time': bi[1],
                               'end_date': bi[2],
                               'end_time': bi[3],
                               'all_day': bi[4]})

        # shouldn't raise error, all day is True, hours ignored
        self.widget.parseFormData({'start_date': '30/11/2010',
                                       'start_time': '8:00',
                                       'end_date': '01/12/2010',
                                       'end_time': '0a:00',
                                       'all_day': 'on'})


class IntervalWidgetSchemaTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Interval widget in a Schema """

    def afterSetUp(self):
        schema = Schema(id='interval_schema', title='Interval Schema')
        self.schema = schema.__of__(self.portal.portal_schemas)
        addIntervalWidget(self.schema, 'theint-property', title='Interval Wid.')

    def test_nothing(self):
        start_date = datetime(2011, 11, 13, 14, 0)
        end_date = datetime(2011, 11, 15, 19, 0)
        form_data, form_errors = self.schema.processForm({
            'theint.start_date': '13/11/2011', 'theint.start_time': '14:00',
            'theint.end_date': '15/11/2011', 'theint.end_time': '19:00',
            'theint.all_day': False})
        self.assertEqual(form_errors, {})
        self.assertEqual(form_data, {'theint': Interval(start_date, end_date,
                                                         False)})
