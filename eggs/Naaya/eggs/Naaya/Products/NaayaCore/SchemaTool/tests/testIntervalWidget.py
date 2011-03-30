# encoding: utf-8
import unittest
from lxml.html.soupparser import fromstring
import re

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
        html = self.widget.render_html(Interval('25/03/2011', '8:00',
                                                '26/03/2011', '08:30', False))
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
        self.assertEqual(output, Interval('30/11/2010', '8:00',
                                          '1/12/2010', '20:00', False))
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

class IntervalWidgetSchemaTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Interval widget in a Schema """

    def afterSetUp(self):
        schema = Schema(id='interval_schema', title='Interval Schema')
        self.schema = schema.__of__(self.portal.portal_schemas)
        addIntervalWidget(self.schema, 'theint-property', title='Interval Wid.')

    def test_nothing(self):
        form_data, form_errors = self.schema.processForm({
            'theint.start_date': '13/11/2011', 'theint.start_time': '14:00',
            'theint.end_date': '15/11/2011', 'theint.end_time': '19:00',
            'theint.all_day': False})
        self.assertEqual(form_errors, {})
        self.assertEqual(form_data, {'theint': Interval('13/11/2011', '14:00',
                                                        '15/11/2011', '19:00',
                                                         False)})
