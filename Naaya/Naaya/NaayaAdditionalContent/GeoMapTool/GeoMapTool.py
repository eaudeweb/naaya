#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "EWGeoMap"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania and Eau de Web 
#are Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#        Bogdan Grama (Finsiel Romania)
#        Iulian Iuga (Finsiel Romania)
#  Porting to Naaya: 
#        Cornel Nitu (Eau de Web)

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.GeoMapTool.constants import *
from Products.NaayaCore.GeoMapTool import gml_to_kml
from Products.NaayaCore.GeoMapTool.managers.symbols_tool import symbols_tool
from Products.NaayaContent import *

def manage_addGeoMapTool(self, REQUEST=None):
    """ """
    ob = GeoMapTool(ID_GEOMAPTOOL, TITLE_GEOMAPTOOL)
    self._setObject(ID_GEOMAPTOOL, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class GeoMapTool(Folder, symbols_tool):
    """ """

    meta_type = METATYPE_GEOMAPTOOL
    icon = 'misc_/GeoMapTool/GeoMapTool.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        symbols_tool.__dict__['__init__'](self)

#    #gml aggregator
    security.declareProtected(view, 'geomap_gml')
    def geomap_gml(self, REQUEST=None):
        """ """
        r = []
        ra = r.append
        ra('<?xml version="1.0" encoding="utf-8"?>')
        ra('<gml:FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://destinet.ewindows.eu.org/schemas/gml_destinet.xsd" xmlns:gml="http://www.opengis.net/gml" xmlns:met="http://destinet.ewindows.eu.org/schemas">')
        filter_types = self.getSession('filter_types', self.getSymbolsIds())
        for ob in self.getCatalogedObjects(meta_type=[METATYPE_NYGEOPOINT], approved=1):
            if ob.geo_type in filter_types:
                ra(ob.exportGmlEntity())
        ra('</gml:FeatureCollection>')
        self.delSession('filter_types')
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
        return ''.join(r)

    security.declareProtected(view, 'symbols_xml')
    def symbols_xml(self, REQUEST=None, RESPONSE=None):
        """ """
        r = []
        ra = r.append
        ra('<?xml version="1.0" encoding="utf-8"?>')
        ra('<symbols>')
        for ob in self.getSymbolsList():
            ra('<symbol>')
            ra('<id>%s</id>' % self.utXmlEncode(ob.id))
            ra('<title>%s</title>' % self.utXmlEncode(ob.title))
            ra('<description>%s</description>' % self.utXmlEncode(ob.description))
            ra('<picture>%s/getSymbolPicture?id=%s</picture>' % (self.absolute_url(), ob.id))
            ra('</symbol>')
        ra('</symbols>')
        RESPONSE.setHeader('Content-Type', 'text/xml')
        return ''.join(r)

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminAddSymbol')
    def adminAddSymbol(self, title='', description='', picture='', REQUEST=None):
        """ """
        self.addSymbol(self.utGenRandomId(3), title, description, picture)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_symbols_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminUpdateSymbol')
    def adminUpdateSymbol(self, id='', title='', description='', picture='', REQUEST=None):
        """ """
        self.updateSymbol(id, title, description, picture)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_symbols_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminDeleteSymbols')
    def adminDeleteSymbols(self, id=[], REQUEST=None):
        """ """
        self.deleteSymbol(self.utConvertToList(id))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_symbols_html' % self.absolute_url())

    #converters related
    security.declareProtected(view, 'GMLtoKML')
    def GMLtoKML(self, gml_file='', schema_file='', REQUEST=None):
        """ """
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/vnd.google-earth.kml+xml')
        REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=destinet.kml')
        return gml_to_kml.gml_to_kml(gml_file, schema_file, self.absolute_url())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/geomap_index', globals())

    security.declareProtected(view, 'pick_html')
    pick_html = PageTemplateFile('zpt/geomap_pick', globals())

    security.declareProtected(view, 'legend')
    legend = PageTemplateFile('zpt/legend', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_symbols_html')
    admin_symbols_html = PageTemplateFile('zpt/geomap_admin_symbols', globals())

InitializeClass(GeoMapTool)