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
# Andrei Laza, Eau de Web

from unittest import TestSuite, makeSuite
import random

from Products.Naaya.tests import NaayaTestCase
from Products.Naaya.tests import NaayaFunctionalTestCase
from Products.NaayaContent.NyGeoPoint.tests.testFunctional import GeoPointMixin

from Products.Naaya.NyFolder import addNyFolder

class GeoClustersTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase, GeoPointMixin):
    symbol_ids = ['symbol1', 'symbol2']
    howmany = 100
    ob_dicts = []

    def afterSetUp(self):
        self.geopoint_install()
        self.portal.setDefaultSearchableContent()

        for id in self.symbol_ids:
            self.portal.portal_map.addSymbol(id, id, '', '', '', '')

        addNyFolder(self.portal, 'geo_clusters_test', contributor='contributor',
                submited=1)
        folder = self.portal.geo_clusters_test

        for i in range(self.howmany):
            ob_dict = dict()
            ob_dict['id'] = 'id_%s' % i
            ob_dict['title'] = 'Title for point %s' % i
            ob_dict['description'] = 'Description for point %s' % i
            ob_dict['geo_location.lat'] = str(random.uniform(-90, 90))
            ob_dict['geo_location.lon'] = str(random.uniform(-180, 180))
            ob_dict['geo_location.address'] = 'Address for point %s' % i
            ob_dict['latitude'] = str(random.uniform(-90, 90))
            ob_dict['longitude'] = str(random.uniform(-180, 180))
            ob_dict['geo_type'] = random.choice(self.symbol_ids)
            ob_dict['URL'] = 'URL for point %s' % i

            ob_dict['id'] = folder.addNyGeoPoint(**ob_dict)
            self.ob_dicts.append(ob_dict)

            ob = self.portal.geo_clusters_test._getOb(ob_dict['id'])
            ob.approveThis()
            self.portal.portal_map.catalogNyObject(ob)

        self.old_geotagged = self.portal.portal_map.list_geotaggable_types()
        schemas = self.portal.portal_schemas.objectValues()
        self.portal.portal_map.admin_set_contenttypes([schema.id for schema in schemas])

    def beforeTearDown(self):
        self.portal.portal_map.admin_set_contenttypes([gt['id'] for gt in self.old_geotagged if gt['enabled']])

        ids = [ob_dict['id'] for ob_dict in self.ob_dicts]
        self.portal.geo_clusters_test.manage_delObjects(ids)

        self.portal.manage_delObjects(['geo_clusters_test'])

        for id in self.symbol_ids:
            self.portal.portal_map.deleteSymbol(id)

        self.geopoint_uninstall()
        self.portal.setDefaultSearchableContent()

    def test_clusters_function(self):
        cl, sg = self.portal.portal_map.search_geo_clusters()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(GeoClustersTestCase))
    return suite
