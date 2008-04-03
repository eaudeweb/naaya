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
#The Original Code is "GeoMapTool"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA). Portions created by Eau de Web are Copyright (C) 
#2007 by European Environment Agency. All Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#Special thanks to Dragos Chirila (fourhooks.com)

#Python imports
import os.path
from cgi import escape

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaCore.managers.session_manager import session_manager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from managers.symbols_tool import symbols_tool
from managers.kml_gen import kml_generator
from managers.csv_reader import CSVReader
from managers.geocoding import location_geocode


def get_template(name):
    f = open(os.path.join(os.path.dirname(__file__), 'templates', name))
    try:
        content = f.read()
    finally:
        f.close()
    return ''.join(("""<script type="text/javascript">\n<!--\n""", content, """\n// -->\n</script>\n/"""))

TEMPLATE_XMLRPC_LOCATIONS_MAP_LOADER = get_template('xmlrpc_locations_map_loader.js')
TEMPLATE_XMLRPC_SIMPLE_MAP_LOADER = get_template('xmlrpc_simple_map_loader.js')
TEMPLATE_XMLRPC_ADDPICK_MAP_LOADER = get_template('xmlrpc_addpick_map_loader.js')
TEMPLATE_XMLRPC_EDITPICK_MAP_LOADER = get_template('xmlrpc_editpick_map_loader.js')


def manage_addGeoMapTool(self, languages=None, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    if languages is None: languages = []
    ob = GeoMapTool(ID_GEOMAPTOOL, TITLE_GEOMAPTOOL)
    self._setObject(ID_GEOMAPTOOL, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class GeoMapTool(Folder, utils, session_manager, symbols_tool):
    """
    Class that implements the tool.
    """

    meta_type = METATYPE_GEOMAPTOOL
    icon = 'misc_/NaayaCore/GeoMapTool.gif'

    security = ClassSecurityInfo()

    manage_options = (
        Folder.manage_options
    )

    _properties = (
        Folder._properties
        +
        (
            {'id':'mapsapikey', 'type': 'string', 'mode': 'w'},
            {'id':'center_locality', 'type': 'string', 'mode': 'w'},
            {'id':'center_zoom', 'type': 'int', 'mode': 'w'},
            {'id':'detailed_zoom', 'type': 'int', 'mode': 'w'},
        )
    )

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        self.mapsapikey = 'm.6kzBLV34FOaYaMCfIKBRHIIYE8zCf6c6yxcc5rZCWkCilWFPzAhcyQEcRTgYKy5g--'
        #center map in Europe
        self.center_locality = MAP_CENTER_LOCALITY
        self.center_zoom = MAP_CENTER_ZOOM
        self.detailed_zoom = MAP_DETAILED_ZOOM
        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT
        self.detailed_map_width = MAP_DETAILED_WIDTH
        self.detailed_map_height = MAP_DETAILED_HEIGHT
        self.map_types = YAHOO_MAP_TYPES
        self.default_type = 'YAHOO_MAP_REG'
        symbols_tool.__dict__['__init__'](self)

    def __setstate__(self,state):
        """Updates"""
        if not hasattr(self, 'map_types'):
            self.map_types = YAHOO_MAP_TYPES
        if not hasattr(self, 'default_type'):
            self.default_type = 'YAHOO_MAP_REG'
        Folder.inheritedAttribute("__setstate__") (self, state)

    #admin actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, mapsapikey='', center_locality='', center_zoom='', detailed_zoom='', map_width='', map_height='', detailed_map_width='', detailed_map_height='', map_types=[], default_type='', REQUEST=None):
        """ """
        try: center_zoom = abs(int(center_zoom))
        except: center_zoom = MAP_CENTER_ZOOM
        try: detailed_zoom = abs(int(detailed_zoom))
        except: detailed_zoom = MAP_DETAILED_ZOOM
        try: map_width = abs(int(map_width))
        except: map_width = MAP_WIDTH
        try: map_height = abs(int(map_height))
        except: map_height = MAP_HEIGHT
        try: detailed_map_width = abs(int(detailed_map_width))
        except: detailed_map_width = MAP_DETAILED_WIDTH
        try: detailed_map_height = abs(int(detailed_map_height))
        except: detailed_map_height = MAP_DETAILED_HEIGHT
        self.mapsapikey = mapsapikey
        self.center_locality = center_locality
        self.center_zoom = center_zoom
        self.detailed_zoom = detailed_zoom
        self.map_width = map_width
        self.map_height = map_height
        self.detailed_map_width = detailed_map_width
        self.detailed_map_height = detailed_map_height
        self.map_types = self.utConvertToList(map_types)
        if not default_type:
            default_type = 'YAHOO_MAP_REG'
        self.default_type = default_type
        self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/admin_map_html' % self.absolute_url())

    security.declareProtected(view, 'locations_kml')
    def locations_kml(self, path='', show='', REQUEST=None):
        """ """
        path = path or '/'
        show = eval(show)

        site_ob = self.getSite()
        output = []
        out_app = output.append

        kml = kml_generator()
        out_app(kml.header())
        out_app(kml.style())
        for loc in site_ob.getCatalogedObjectsCheckView(meta_type='Naaya GeoPoint', geo_type=show, path=path):
            if loc.latitude != 0.0 and loc.longitude != 0.0:
                out_app(kml.add_point(self.utToUtf8(loc.id),
                                      self.utXmlEncode(loc.title),
                                      self.utXmlEncode(loc.description),
                                      '%s/getSymbolPicture?id=%s' % (self.absolute_url(), self.utToUtf8(loc.geo_type)),
                                      self.utToUtf8(loc.longitude),
                                      self.utToUtf8(loc.latitude),
                                      self.utXmlEncode(self.getSymbolTitle(loc.geo_type)),
                                      self.utToUtf8(self.absolute_url()),
                                      self.utToUtf8(loc.absolute_url()),
                                      self.utToUtf8(loc.url),
                                      self.utXmlEncode(loc.address)))
        out_app(kml.footer())
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/vnd.google-earth.kml+xml')
        REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=locations.kml')
        return '\n'.join(output)

    security.declareProtected(view, 'xrjs_feed')
    def xrjs_feed(self, key, show, query, path, REQUEST):
        """ """
        r, i = [], ''
        t = []
        ra = r.append
        #if key == self.getSession(MSP_SESSION_KEY, None):
        portal_ob = self.getSite()
        if show:
            show = eval(show)
            results = portal_ob.getCatalogedObjectsCheckView(meta_type='Naaya GeoPoint', geo_type=show, path=path)
            for res in results:
                if res.latitude != 0.0 and res.longitude != 0.0:
                    ra('%s|%s|mk_%s|%s|%s' % (self.utToUtf8(res.latitude),
                                              self.utToUtf8(res.longitude),
                                              self.utToUtf8(res.id),
                                              self.utToUtf8(self.utJavaScriptEncode(res.title_or_id())),
                                              'mk_%s' % self.utToUtf8(res.geo_type)))
                    t.append(res.marker_html())
        i = ''.join(t)
        #self.delSession(MSP_SESSION_KEY)
        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return '%s\n\n%s' % ('\n'.join(r), i)

    security.declareProtected(view, 'xrjs_simple_feed')
    def xrjs_simple_feed(self, key, show, REQUEST):
        """ """
        #if key == self.getSession(MSP_SESSION_KEY, None):
        res = ''
        ob = self.unrestrictedTraverse('%s' % show)
        if ob:
            if ob.latitude != 0.0 and ob.longitude != 0.0:
                res = '%s|%s|%s' % (ob.latitude, ob.longitude, self.utJavaScriptEncode(ob.title_or_id()))
        #self.delSession(MSP_SESSION_KEY)
        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return res

    security.declareProtected(view, 'xrjs_markers')
    def xrjs_markers(self):
        #load markers on the map
        output = []
        out_a = output.append
        for symbol in self.getSymbolsList():
            out_a("mk_%s = new YImage();" % symbol.id)
            icon_url = '%s/getSymbolPicture?id=%s' % (self.absolute_url(), symbol.id)
            if icon_url is not None:
                out_a('mk_%s.src = "%s";' % (symbol.id, icon_url))
                out_a('mk_%s.size = new YSize(22, 22);' % symbol.id)
                out_a('mk_%s.offsetSmartWindow = new YCoordPoint(6, 11);' % symbol.id)
        return '\n'.join(output)

    #xmlrpc interface
    def xrjs_loader(self, show, query, center='', zoom='', path='', width='', height=''):
        #initialize markers loader - locations
        xr_key = self.utGenRandomId(32)
        show = self.utJsEncode(show)
        self.setSession(MSP_SESSION_KEY, xr_key)
        #try to get the coordinates from request
        center_locality = center or self.center_locality
        if center_locality.startswith("YGeoPoint"):
            center_locality = 'new ' + center_locality # YGeoPoint object
        else:
            center_locality = '"' + center_locality + '"' # Javascript string
        center_zoom = zoom or self.center_zoom
        path = path or '/'
        return TEMPLATE_XMLRPC_LOCATIONS_MAP_LOADER % (center_locality, center_zoom, self.default_type, width, height, ",".join(self.map_types), self.xrjs_markers(), self.absolute_url(), xr_key, show, query, path)

    def xrjs_simple_loader(self, show):
        #initialize marker loader - location
        xr_key = self.utGenRandomId(32)
        show = self.utJsEncode(show)
        self.setSession(MSP_SESSION_KEY, xr_key)
        ob = self.unrestrictedTraverse('%s' % show)
        center_locality, center_zoom = self.center_locality, self.center_zoom
        if ob:
            center_latitude, center_longitude = 0.0, 0.0
            if ob.latitude != 0.0 and ob.longitude != 0.0:
                center_latitude, center_longitude, center_zoom = ob.latitude, ob.longitude, self.detailed_zoom
        return TEMPLATE_XMLRPC_SIMPLE_MAP_LOADER % (center_latitude, center_longitude, center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types), self.get_location_marker(ob), self.absolute_url(), xr_key, show)

    def xrjs_editpick_loader(self, show):
        #initialize edit pick map
        show = self.utJsEncode(show)
        ob = self.unrestrictedTraverse('%s' % show)
        if ob:
            latitude, longitude, zoom = ob.latitude, ob.longitude, self.detailed_zoom
        return TEMPLATE_XMLRPC_EDITPICK_MAP_LOADER % (latitude, longitude, zoom, self.center_locality, self.center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types))

    def xrjs_addpick_loader(self):
        #initialize add pick map
        center_locality, center_zoom = self.center_locality, self.center_zoom + 2
        return TEMPLATE_XMLRPC_ADDPICK_MAP_LOADER % (center_locality, center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types))

    def get_location_marker(self, location):
        symbol = self.getSymbol(location.geo_type)
        if symbol:
            icon_url = '%s/getSymbolPicture?id=%s' % (self.absolute_url(), symbol.id)
            if icon_url is not None:
                return icon_url
            return ''
        return ''

    security.declarePrivate('add_location')
    def add_location(self, title, description, address, URL, approved, container, geo_type, latitude, longitude):
        """ add a location in the database """
        from Products.NaayaContent.NyGeoPoint.NyGeoPoint import addNyGeoPoint
        meta_type = 'Naaya GeoPoint'

        if latitude.strip() == '' and longitude.strip() == '':
            coordinates = location_geocode(address)
            if coordinates is None:
                latitude, longitude = (0.0, 0.0)
            else:
                latitude, longitude = coordinates

        parent_ob = self.utGetObject(container)

        if meta_type in parent_ob.get_pluggable_installed_meta_types():
            try:
                addNyGeoPoint(parent_ob, title=title, description=description, coverage='', keywords='', sortorder='', longitude=longitude, latitude=latitude, address=address, geo_type=geo_type, url=URL)
            except Exception, err:
                return 'Failed to add %s geo-point! Error: %s' % (title, str(err))

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'uploadLocations')
    def uploadLocations(self, file='', dialect='comma', encoding='utf-8', approved=0, parent_folder='', geo_type='', REQUEST=None):
        """ """
        if file.filename.find('\\') != -1:
            filename = file.filename.split('\\')[-1]
        else:
            filename = file.filename

        metadata = ['name', 'description', 'address', 'URL', 'latitude', 'longitude']
        errs = []

        #step 1. read the CSV file
        csv = CSVReader(file, dialect, encoding)
        records, error = csv.read()

        #validate metadata
        for meta in metadata:
            if meta not in records[0].keys():
                errs.append('Invalid headers in file!')

        #step 2. add locations
        for rec in records:
            if rec:
                err = self.add_location(self.utToUnicode(rec['name']),
                                        self.utToUnicode(rec['description']),
                                        rec['address'],
                                        rec.get('URL', ''),
                                        approved,
                                        parent_folder,
                                        geo_type,
                                        rec.get('latitude', ''),
                                        rec.get('longitude', ''))
                if err is not None:
                    errs.append(err)

        if errs:
            self.setSessionErrors(errs)
        else:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        return REQUEST.RESPONSE.redirect('%s/admin_mapupload_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getLocations')
    def getLocations(self, skey='', rkey=''):
        """ return the list of locations """
        r = self.getCatalogedObjects(meta_type=['Naaya GeoPoint'])
        if skey in ['title', 'address', 'latitude', 'longitude']:
            r = self.utSortObjsListByAttr(r, skey, rkey)
        return r

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteLocations')
    def deleteLocations(self, locations, REQUEST=None):
        """ delete locations """
        for location in locations:
            loc_obj = self.unrestrictedTraverse(location, None)
            if loc_obj:
                loc_obj.getParentNode().manage_delObjects([loc_obj.id])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maplocations_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminAddSymbol')
    def adminAddSymbol(self, title='', description='', parent='', picture='', REQUEST=None):
        """ """
        self.addSymbol('symbol%s' % self.utGenRandomId(3), title, description, parent, picture)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminUpdateSymbol')
    def adminUpdateSymbol(self, id='', title='', description='', parent='', picture='', REQUEST=None):
        """ """
        self.updateSymbol(id, title, description, parent, picture)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminDeleteSymbols')
    def adminDeleteSymbols(self, id=[], REQUEST=None):
        """ """
        self.deleteSymbol(self.utConvertToList(id))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSymbolsListOrdered')
    def getSymbolsListOrdered(self, skey='', rkey=''):
        """ return an ordered lsit of symbols """
        r = self.getSymbolsList()
        if skey in ['title', 'parent']:
            r = self.utSortObjsListByAttr(r, skey, rkey)
        return r

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if hasattr(self, 'map_index'):
            return self._getOb('map_index')({'here': self})
        return self.view_map_html({'here': self})

    security.declareProtected(view, 'view_map_html')
    view_map_html = PageTemplateFile('zpt/map_index', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_map_html')
    admin_map_html = PageTemplateFile('zpt/map_edit', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_maptypes_html')
    admin_maptypes_html = PageTemplateFile('zpt/map_symbols', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_mapupload_html')
    admin_mapupload_html = PageTemplateFile('zpt/map_upload', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_maplocations_html')
    admin_maplocations_html = PageTemplateFile('zpt/map_locations', globals())

    security.declareProtected(view_management_screens, 'update_geomap_27022008')
    def update_geomap_27022008(self):
        """ """
        self.map_types = YAHOO_MAP_TYPES
        self.default_type = 'YAHOO_MAP_REG'
        self._p_changed = 1
        return 'Done'

    # macros
    security.declareProtected(view, 'locations_table_html')
    locations_table_html = PageTemplateFile('zpt/locations_table', globals())

InitializeClass(GeoMapTool)
