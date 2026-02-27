# encoding: utf-8
import unittest
from decimal import Decimal

from Products.NaayaCore.SchemaTool.Schema import Schema
from Products.NaayaCore.SchemaTool.widgets.GeoWidget import (
    Geo, GeoWidget, addGeoWidget, WidgetError)
from Products.Naaya.tests import NaayaTestCase

class GeoTestCase(unittest.TestCase):
    """ TestCase for Geo data type """

    def test_create_blank(self):
        g = Geo()
        self.assertTrue(g.lat is None)
        self.assertTrue(g.lon is None)
        self.assertTrue(isinstance(g.address, str))
        self.assertEqual(g.address, '')
        self.assertTrue(g.missing_lat_lon is True)

    def test_create(self):
        g = Geo(13, '17.223', '13 Naaya Bd.')
        self.assertTrue(isinstance(g.lon, Decimal))
        self.assertTrue(isinstance(g.lat, Decimal))
        self.assertTrue(isinstance(g.address, str))
        self.assertEqual(g.lat, 13)
        self.assertEqual(g.lon, Decimal('17.223'))
        self.assertEqual(g.address, '13 Naaya Bd.')
        self.assertTrue(g.missing_lat_lon is False)

    def test_create_no_coords(self):
        g = Geo(address='hello world')
        self.assertEqual(g.lat, None)
        self.assertEqual(g.lon, None)
        self.assertEqual(g.address, u'hello world')
        self.assertTrue(g.missing_lat_lon is True)

    def test_create_one_coord(self):
        # When one coord is None and the other isn't, Geo normalizes both
        # to None (with a warning) to avoid broken geo data in ZODB
        g = Geo(13, None)
        self.assertIsNone(g.lat)
        self.assertIsNone(g.lon)

    def test_create_error(self):
        try:
            Geo('1.2.3', '13')
            self.fail('should raise exception')
        except ValueError as e:
            self.assertTrue('Bad value "1.2.3" for latitude')

    def test_repr(self):
        g = Geo(13, '17.223')
        self.assertEqual(repr(g), "Geo(lat=13, lon=17.223)")
        g = Geo(13, '17.223', '13 Naaya Bd.')
        self.assertEqual(repr(g), "Geo(lat=13, lon=17.223, "
            "address='13 Naaya Bd.')")
        g = Geo(address='13 Naaya Bd.')
        self.assertEqual(repr(g), "Geo(lat=None, lon=None, "
            "address='13 Naaya Bd.')")
        g = Geo(address='39 N\u0434a\u2139\u03b1 road')
        self.assertIn('39 N', repr(g))
        self.assertIn('road', repr(g))

class GeoWidgetTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Geo widget """

    def afterSetUp(self):
        widget = GeoWidget('geo-property', title='Geo Location', lang='en')
        self.widget = widget.__of__(self.portal.portal_schemas.NyDocument)

    def test_edit_form(self):
        html = self.widget.render_html(Geo(3, 5, 'here!'))
        self.assertTrue('value="3"' in html)
        self.assertTrue('value="5"' in html)
        self.assertTrue('value="here!"' in html)

    def test_parse_data(self):
        output = self.widget.parseFormData({'lat': '13',
            'lon': '15', 'address': 'Somewhere'})
        self.assertTrue(isinstance(output, Geo))
        self.assertEqual(output, Geo(13, 15, 'Somewhere'))
        self.assertEqual(Geo(13, 15),
            self.widget.parseFormData({'lat': '13', 'lon': '15'}))
        self.assertEqual(self.widget.parseFormData(''), None)

    def test_parse_bad_data(self):
        try:
            self.widget.parseFormData({'lat': '13.57', 'lon': '1.2.3'})
            self.fail('should raise exception')
        except WidgetError as e:
            self.assertTrue("Bad value \'1.2.3\' for longitude" in str(e))

class GeoWidgetSchemaTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Geo widget in a Schema """

    def afterSetUp(self):
        schema = Schema(id='geo_schema', title='Geo Schema')
        self.schema = schema.__of__(self.portal.portal_schemas)
        addGeoWidget(self.schema, 'thegeo-property', title='Geo Location')

    def test_nothing(self):
        form_data, form_errors = self.schema.processForm({
            'thegeo.lat': '13', 'thegeo.lon': '14'})
        self.assertEqual(form_errors, {})
        self.assertEqual(form_data, {'thegeo': Geo(13, 14)})
