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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

# Product imports
from Products.NaayaCore.GeoMapTool.managers import geocoding
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaWidgets.Widget import Widget, WidgetError, manage_addWidget
from Products.NaayaCore.SchemaTool.widgets.geo import Geo, geo_as_json


def addGeoWidget(container, id="", title="Geo Widget", REQUEST=None, **kwargs):
    """ Contructor for Geo widget"""
    return manage_addWidget(GeoWidget, container, id, title, REQUEST, **kwargs)

class GeoWidget(Widget):
    """Geo Widget"""

    meta_type = "Naaya Geo Widget"
    meta_label = "Geographical location"
    meta_description = "A pair of coordinates and an address"
    meta_sortorder = 600
    icon_filename = 'widgets/www/widget_geo.gif'

    _properties = Widget._properties + ()

    # Constructor
    _constructors = (addGeoWidget,)
    render_meth = PageTemplateFile('zpt/widget_geo.zpt', globals())

    def coord_as_json(self, value):
        return geo_as_json(value)

    def getDatamodel(self, form):
        """Get datamodel from form"""
        lat = form.get(self.getWidgetId() + '.lat', None)
        lon = form.get(self.getWidgetId() + '.lon', None)
        address = form.get(self.getWidgetId() + '.address', '')
        if not (lat and lon):
            coordinates = geocoding.location_geocode(address)
            if coordinates is not None:
                lat, lon = coordinates
        if not lat:
            lat = None
        if not lon:
            lon = None

        if lat is None and lon is None and address == '':
            return None

        try:
            return Geo(lat, lon, address)
        except ValueError:
            raise WidgetError('Invalid geo values for "%s"' % self.title)

    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if datamodel is None:
            return self._get_default_value()
        return '%r' % (datamodel,)

InitializeClass(GeoWidget)

def register():
    return GeoWidget
