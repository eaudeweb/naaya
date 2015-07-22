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
# Alin Voinea, Eau de Web
# Alex Morega, Eau de Web

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addGeoTypeWidget(container, id="", title="Select Widget", REQUEST=None, **kwargs):
    """ Contructor for Select widget"""
    return manage_addWidget(GeoTypeWidget, container, id, title, REQUEST, **kwargs)

class GeoTypeWidget(Widget):
    """ Select Widget """

    meta_type = "Naaya Geo Type Widget"
    meta_label = "Select map marker"
    meta_description = "Value selection from list of map markers"
    meta_sortorder = 150

    # Constructor
    _constructors = (addGeoTypeWidget,)

    def isEmptyDatamodel(self, value):
        return not bool(value)

    def _convert_to_form_string(self, value):
        if isinstance(value, int):
            value = str(value)
        return value

    def convert_from_user_string(self, value):
        """ Convert a user-readable string to a value that can be saved """
        geo_map_tool = self.getSite().getGeoMapTool()
        for symbol in geo_map_tool.getSymbolsList():
            if value == symbol.title:
                return symbol.id
        raise ValueError('Could not convert value %s' % repr(value))

    def convert_to_user_string(self, value):
        """ Convert a database value to a user-readable string """
        geo_map_tool = self.getSite().getGeoMapTool()
        for symbol in geo_map_tool.getSymbolsList():
            if value == symbol.id:
                return symbol.title
        raise ValueError('Could not convert value %s' % repr(value))

    template = PageTemplateFile('../zpt/property_widget_geo_type', globals())
