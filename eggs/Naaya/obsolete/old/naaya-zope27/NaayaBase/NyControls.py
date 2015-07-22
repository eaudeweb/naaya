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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Eau de Web
# Cristian Romanescu, Eau de Web
# David Batranu, Eau de Web

"""
This module contains the class that provides control elements.
"""

#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass

#Product imports
from constants import *
from NyCheckControl import NyCheckControl

class NyMapControl:
    """
    The base class of Naaya Map control. It implements basic functionality
    common to all classes.
    """

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Initialize variables:

        B{longitude} - longitude
        B{latitude} - latitude
        B{geo_address} - address
        """
        self.longitude = getattr(self, 'longitude', '')
        self.latitude =  getattr(self, 'latitude', '')
        self.address =   getattr(self, 'address', '')
        self.url =       getattr(self, 'url', '')
        self.geo_type =  getattr(self, 'geo_type', '')

    def setMapValues(self):
        """ """
        for name in self.get_props():
            try:    del(self.__dynamic_properties[name])
            except: pass

    def get_props(self):
        return ['longitude', 'latitude', 'address', 'url', 'geo_type']

    security.declareProtected(view, 'marker_html')
    def marker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        #TODO: create marker template(s)
        return """
<div class="marker-body">
    <h3>%s</h3>
    <small>%s</small>
    <div class="marker-more">
        <a href="%s" i18n:translate="">see more</a>
    </div>
</div>
        """ % (self.utToUtf8(self.title_or_id()), self.utTruncateString(self.utToUtf8(self.description), 130), self.absolute_url())

    #zmi pages
    security.declareProtected(view, 'map_widget_add_html')
    map_widget_add_html = PageTemplateFile('zpt/map_widget_add', globals())

    security.declareProtected(view, 'map_widget_edit_html')
    map_widget_edit_html = PageTemplateFile('zpt/map_widget_edit', globals())

    security.declareProtected(view, 'map_widget_index_html')
    map_widget_index_html = PageTemplateFile('zpt/map_widget_index', globals())

InitializeClass(NyMapControl)
