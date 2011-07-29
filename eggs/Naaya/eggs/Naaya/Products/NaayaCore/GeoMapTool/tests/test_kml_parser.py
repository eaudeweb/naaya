from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

from Products.NaayaCore.GeoMapTool.managers.kml_parser import parse_kml


def load_file(filename):
    import os
    from StringIO import StringIO
    from Globals import package_home
    filename = os.path.sep.join([package_home(globals()), filename])
    data = StringIO(open(filename, 'rb').read())
    data.filename = os.path.basename(filename)
    return data

class KMLParserTestCase(ZopeTestCase.TestCase):

    def afterSetUp(self):
        pass

    def beforeTearDown(self):
        pass

    def test_parse(self):
        kml_file = load_file('data/kml_export.kml')
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
