from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget
from geo import Geo, geo_as_json
from Products.NaayaCore.GeoMapTool.managers import geocoding

def addGeoWidget(container, id="", title="Geo Widget", REQUEST=None, **kwargs):
    """ Contructor for Geo widget"""
    return manage_addWidget(GeoWidget, container, id, title, REQUEST, **kwargs)

class GeoWidget(Widget):
    """ Geo Widget """

    meta_type = "Naaya Schema Geo Widget"
    meta_label = "Latitude, longitude and address"
    meta_description = "Represents a geographical location - coordinates and street address"
    meta_sortorder = 150

    # Constructor
    _constructors = (addGeoWidget,)

    multiple_form_values = ('lat', 'lon', 'address')
    default = None

    def parseFormData(self, data):
        if self.isEmptyDatamodel(data):
            return None

        if isinstance(data, Geo):
            return data

        if not isinstance(data, dict):
            raise WidgetError('Expected multiple values for "%s"' % self.title)

        try:
            lat = data.get('lat', None)
            if not lat:
                lat = None
            lon = data.get('lon', None)
            if not lon:
                lon = None
            address = data.get('address', '').strip()
            if address and lat is lon is None:
                coordinates = geocoding.location_geocode(address)
                if coordinates is not None:
                    lat, lon = coordinates
            return Geo(lat, lon, address)
        except ValueError, e:
            raise WidgetError(str(e))

    def coord_as_json(self, value):
        return geo_as_json(value)

    def isEmptyDatamodel(self, value):
        return value in (None, '', {}, Geo())

    def convertValue(self, value):
        if not (value is None or isinstance(value, Geo)):
            raise WidgetError('Bad value for GeoWidget: %s' % repr(value))
        elif value == Geo():
            return None
        else:
            return value

    def _convert_to_form_string(self, value):
        """
        We don't actually convert to a string here; GeoWidget needs the Geo
        instance all the way to the template
        """
        if value == Geo():
            return None
        return value

    hidden_template = PageTemplateFile('../zpt/property_widget_hidden_geo', globals())

    template = PageTemplateFile('../zpt/property_widget_geo', globals())

InitializeClass(GeoWidget)
