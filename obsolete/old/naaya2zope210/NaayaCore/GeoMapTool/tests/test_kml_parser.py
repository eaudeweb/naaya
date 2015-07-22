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
# David Batranu, Eau de Web

from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

from Products.NaayaCore.GeoMapTool.managers.kml_parser import parse_kml
from Products.Naaya.tests.NaayaTestCase import load_test_file


class KMLParserTestCase(ZopeTestCase.TestCase):

    def afterSetUp(self):
        pass

    def beforeTearDown(self):
        pass

    def test_parse(self):
        kml_file = load_test_file('data/kml_export.kml', globals())
        expected_data = [{'name': u'Bucharest',
                          'description': u'Bucharest description',
                          'latitude': u'44.31693022912877',
                          'longitude': u'25.68361842517931'},

                         {'name': u'Prague',
                          'description': u'Prague description',
                          'latitude': u'50.16784182573986',
                          'longitude': u'14.51580418937693',
                          },

                         {'name': u'Copenhagen',
                          'description': u'Copenhagen description',
                          'latitude': u'55.76806626940991',
                          'longitude': u'12.59385459456745',
                          }]
        parsed_data = parse_kml(kml_file)

        self.failUnless(parsed_data, 'KML parser returned no data')

        for location in parsed_data:
            index = parsed_data.index(location)
            for key in location.keys():
                self.failUnlessEqual(location[key], expected_data[index][key])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(KMLParserTestCase))
    return suite
