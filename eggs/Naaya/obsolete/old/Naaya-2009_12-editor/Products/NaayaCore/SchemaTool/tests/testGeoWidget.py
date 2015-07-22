# encoding: utf-8
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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

from unittest import TestSuite, makeSuite
from decimal import Decimal

from Testing import ZopeTestCase

from Products.NaayaCore.SchemaTool.Schema import Schema
from Products.NaayaCore.SchemaTool.widgets.GeoWidget import (
    Geo, GeoWidget, addGeoWidget, WidgetError)
from Products.Naaya.tests import NaayaTestCase

class GeoTestCase(ZopeTestCase.TestCase):
    """ TestCase for Geo data type """

    def test_create_blank(self):
        g = Geo()
        self.failUnless(g.lat is None)
        self.failUnless(g.lon is None)
        self.failUnless(isinstance(g.address, unicode))
        self.failUnlessEqual(g.address, '')
        self.failUnless(g.missing_lat_lon is True)

    def test_create(self):
        g = Geo(13, '17.223', '13 Naaya Bd.')
        self.failUnless(isinstance(g.lon, Decimal))
        self.failUnless(isinstance(g.lat, Decimal))
        self.failUnless(isinstance(g.address, unicode))
        self.failUnlessEqual(g.lat, 13)
        self.failUnlessEqual(g.lon, Decimal('17.223'))
        self.failUnlessEqual(g.address, '13 Naaya Bd.')
        self.failUnless(g.missing_lat_lon is False)

    def test_create_no_coords(self):
        g = Geo(address='hello world')
        self.failUnlessEqual(g.lat, None)
        self.failUnlessEqual(g.lon, None)
        self.failUnlessEqual(g.address, u'hello world')
        self.failUnless(g.missing_lat_lon is True)

    def test_create_one_coord(self):
        self.failUnlessRaises(ValueError, lambda: Geo(13, None))

    def test_create_error(self):
        try:
            Geo('1.2.3', '13')
            self.fail('should raise exception')
        except ValueError, e:
            self.failUnless('Bad value "1.2.3" for latitude')

    def test_repr(self):
        g = Geo(13, '17.223')
        self.assertEqual(repr(g), "Geo(lat=13, lon=17.223)")
        g = Geo(13, '17.223', '13 Naaya Bd.')
        self.assertEqual(repr(g), "Geo(lat=13, lon=17.223, "
            "address=u'13 Naaya Bd.')")
        g = Geo(address='13 Naaya Bd.')
        self.assertEqual(repr(g), "Geo(lat=None, lon=None, "
            "address=u'13 Naaya Bd.')")
        g = Geo(address=u'39 N\u0434a\u2139\u03b1 road')
        self.assertEqual(repr(g), "Geo(lat=None, lon=None, "
            r"address=u'39 N\u0434a\u2139\u03b1 road')")

class GeoWidgetTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Geo widget """

    def afterSetUp(self):
        widget = GeoWidget('geo-property', title='Geo Location', lang='en')
        self.widget = widget.__of__(self.portal.portal_schemas.NyDocument)

    def test_edit_form(self):
        html = self.widget.render_html(Geo(3, 5, 'here!'))
        self.failUnless('value="3"' in html)
        self.failUnless('value="5"' in html)
        self.failUnless('value="here!"' in html)

    def test_parse_data(self):
        output = self.widget.parseFormData({'lat': '13',
            'lon': '15', 'address': 'Somewhere'})
        self.failUnless(isinstance(output, Geo))
        self.failUnlessEqual(output, Geo(13, 15, 'Somewhere'))
        self.failUnlessEqual(Geo(13, 15),
            self.widget.parseFormData({'lat': '13', 'lon': '15'}))
        self.failUnlessEqual(self.widget.parseFormData(''), None)

    def test_parse_bad_data(self):
        try:
            self.widget.parseFormData({'lat': '13.57', 'lon': '1.2.3'})
            self.fail('should raise exception')
        except WidgetError, e:
            self.failUnless("Bad value \'1.2.3\' for longitude" in str(e))

class GeoWidgetSchemaTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Geo widget in a Schema """

    def afterSetUp(self):
        schema = Schema(id='geo_schema', title='Geo Schema')
        self.schema = schema.__of__(self.portal.portal_schemas)
        addGeoWidget(self.schema, 'thegeo-property', title='Geo Location')

    def test_nothing(self):
        form_data, form_errors = self.schema.processForm({
            'thegeo.lat': '13', 'thegeo.lon': '14'})
        self.failUnlessEqual(form_errors, {})
        self.failUnlessEqual(form_data, {'thegeo': Geo(13, 14)})

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(GeoTestCase))
    suite.addTest(makeSuite(GeoWidgetTestCase))
    suite.addTest(makeSuite(GeoWidgetSchemaTestCase))
    return suite
