from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.geopoint.geopoint_item import addNyGeoPoint
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

class GeoPointCommonTest(_CommonContentTest):

    def add_object(self, parent):
        kwargs = {'title': 'My geopoint', 'geo_location': Geo('13', '13')}
        ob = parent[addNyGeoPoint(parent, **kwargs)]
        ob.approveThis()
        return ob
