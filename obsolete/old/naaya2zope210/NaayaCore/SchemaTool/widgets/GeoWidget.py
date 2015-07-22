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

import simplejson as json

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget
from geo import Geo

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
            address = data.get('address', '')
            return Geo(lat, lon, address)
        except ValueError, e:
            raise WidgetError(str(e))

    def portal_map_config_js(self):
        portal_map = self.getSite().getGeoMapTool()
        js_template = (
            "var prop_name = '%(prop_name)s';\n"
            "var server_base_url = '%(server_base_url)s';\n"
        )
        return js_template % {
            'prop_name': self.prop_name(),
            'server_base_url': portal_map.absolute_url(),
        }

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

    template = PageTemplateFile('../zpt/property_widget_geo', globals())

InitializeClass(GeoWidget)
