from naaya.content.base.tests.common import _IconTests
from naaya.content.geopoint.geopoint_item import addNyGeoPoint
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

class GeoPointIconTests(_IconTests):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya GeoPoint')
        kwargs = {'title': 'My geopoint', 'geo_location': Geo('13', '13')}
        ob = parent[addNyGeoPoint(parent, **kwargs)]
        ob.approveThis()
        return ob
