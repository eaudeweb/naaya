from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from naaya.content.geopoint.geopoint_item import addNyGeoPoint
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

class GeoPointIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya GeoPoint')
        kwargs = {'title': 'My geopoint', 'geo_location': Geo('13', '13')}
        ob = parent[addNyGeoPoint(parent, **kwargs)]
        ob.approveThis()
        return ob
