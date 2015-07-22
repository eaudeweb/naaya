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
#Cristian Romanescu (Eau de Web) added support for Google Maps API

#Python imports
import os.path

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from zLOG import LOG, DEBUG, INFO, ERROR

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils, findDuplicates
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
    return ''.join(("""<script type="text/javascript">\n<!--\n""", content, """\n// -->\n</script>\n"""))

TEMPLATE_XMLRPC_LOCATIONS_MAP_LOADER = 'xmlrpc_locations_map_loader.js'
TEMPLATE_XMLRPC_SIMPLE_MAP_LOADER = 'xmlrpc_simple_map_loader.js'
TEMPLATE_XMLRPC_ADDPICK_MAP_LOADER = 'xmlrpc_addpick_map_loader.js'
TEMPLATE_XMLRPC_EDITPICK_MAP_LOADER = 'xmlrpc_editpick_map_loader.js'

class GeoMapToolUploadError(Exception):
    """GeoMapTool Upload Error"""
    pass

def manage_addGeoMapTool(self, languages=None, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    if languages is None: languages = []
    ob = GeoMapTool(ID_GEOMAPTOOL, TITLE_GEOMAPTOOL)
    self._setObject(ID_GEOMAPTOOL, ob)
    ob = self._getOb(ID_GEOMAPTOOL)
    ob.manage_configureSite()
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
        self.googleApiKey = 'ABQIAAAAkblOrSS9iVzkKUfXj3gOFRR26BjrSmLtamIPMRgDuTUxZh8BLxQ2qfb6PUeks1ZMeSmUGC0ZTrNFVg'
        self.map_engine = 'yahoo'
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
        self.enableKeyControls = True

    def __setstate__(self,state):
        """Updates"""
        if not hasattr(self, 'map_types'):
            self.map_types = YAHOO_MAP_TYPES
        if not hasattr(self, 'map_engine'):
            self.map_engine = 'yahoo'
        if not hasattr(self, 'googleApiKey'):
            self.googleApiKey = ''
        if not hasattr(self, 'default_type'):
            self.default_type = 'YAHOO_MAP_REG'
        if not hasattr(self, 'enableKeyControls'):
            self.enableKeyControls = True
        Folder.inheritedAttribute("__setstate__") (self, state)

    #admin actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'manageProperties')
    def manageProperties(self, mapsapikey='', googleApiKey='', map_engine='', center_locality='', center_zoom='', detailed_zoom='', map_width='', map_height='', detailed_map_width='', detailed_map_height='', map_types=[], default_type='', enableKeyControls='', REQUEST=None):
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
        self.googleApiKey = googleApiKey
        self.map_engine = map_engine
        self.center_locality = center_locality
        self.center_zoom = center_zoom
        self.detailed_zoom = detailed_zoom
        self.map_width = map_width
        self.map_height = map_height
        self.detailed_map_width = detailed_map_width
        self.detailed_map_height = detailed_map_height
        self.map_types = self.utConvertToList(map_types)
        if enableKeyControls: self.enableKeyControls = True
        else: self.enableKeyControls = False
        if not default_type:
            default_type = 'YAHOO_MAP_REG'
        self.default_type = default_type
        self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/admin_map_html' % self.absolute_url())


    #
    # Methods for configuring the Naaya Site for GeoMapTool
    #

    security.declareProtected(PERMISSION_ADMINISTRATE, 'manage_configureCatalog')
    def manage_configureCatalog(self):
        """Configure catalog tool:
            - adds geo_type and address indexes if they don't exist
              and if not, it reindexes them
        """
        catalog_tool = self.getSite().getCatalogTool()
        LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', INFO,
            'Configuring catalog %s for GeoMapTool' % catalog_tool.absolute_url(1))
        new_indexes = []
        # geo_type
        if 'geo_type' not in catalog_tool.indexes():
            LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG,
                'manage_configureCatalog: adding geo_type index to catalog %s' % catalog_tool.absolute_url(1))
            catalog_tool.addIndex('geo_type', 'FieldIndex')
            new_indexes.append('geo_type')
        else:
            LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG,
                'manage_configureCatalog: geo_type index already exists in catalog %s' % catalog_tool.absolute_url(1))
        # address
        if 'address' not in catalog_tool.indexes():
            LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG,
                'manage_configureCatalog: adding address index to catalog %s' % catalog_tool.absolute_url(1))
            catalog_tool.addIndex('address', 'TextIndexNG2',
                                  extra={'default_encoding': 'utf-8',
                                         'splitter_single_chars': True,
                                         'splitter_casefolding': True})
            new_indexes.append('address')
        else:
            LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG,
                'manage_configureCatalog: address index already exists in catalog %s' % catalog_tool.absolute_url(1))
        # reindexing
        if new_indexes:
            LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG,
                'manage_configureCatalog: reindexing indexes %s of catalog %s' % \
                        (new_indexes, catalog_tool.absolute_url(1)))
            catalog_tool.manage_reindexIndex(ids=new_indexes)
        else:
            LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG,
                'manage_configureCatalog: no need to reindex catalog %s because no indexes were added' % catalog_tool.absolute_url(1))

    security.declareProtected(PERMISSION_ADMINISTRATE, 'manage_configureSite')
    def manage_configureSite(self, REQUEST=None):
        """Configures the Naaya Site for GeoMapTool"""
        self.manage_configureCatalog()


    security.declareProtected(view, 'searchGeoPoints')
    def searchGeoPoints(self, path='', geo_types=None, query='', approved=True, landscape_type=[], administrative_level=[], REQUEST=None):
        """Returns all the GeoPoints that match the specified criteria.

            @param path: where to search
            @type path: string
            @param geo_types: the list of geo types to search;
                              if None all geo types are searched
            @type geo_types: list
            @param query: the text that's searched in the title, address and keywords fields;
                          a match of one field is enough
            @type query: string
            @param approved: if True return only approved items, otherwise return all items
            @type approved: bool
            @param REQUEST: REQUEST
            @type REQUEST: REQUEST
            @return: all the GeoPoints that match the specified criteria.
            @rtype: list
        """
        from Products.NaayaContent.NyGeoPoint.NyGeoPoint import NyGeoPoint # TODO move outside method

        meta_list = [NyGeoPoint.meta_type]
        for meta in self.getControlsTool().settings.keys():
            meta_list.append(meta)

        site_ob = self.getSite()
        results = []

        base_kw = {'approved': approved}

        if geo_types:
            base_kw['geo_type'] = geo_types

        if landscape_type:
            base_kw['landscape_type'] = landscape_type

        if administrative_level:
            base_kw['administrative_level' ] = administrative_level

        if query:
            #results.extend(site_ob.getCatalogedMapObjects(meta_type=meta_list, path=path, title=query, **base_kw))
            #results.extend(site_ob.getCatalogedMapObjects(meta_type=meta_list, path=path, address=query, **base_kw))
            results.extend(site_ob.getCatalogedObjectsCheckView(meta_type=meta_list, path=path, title=query, **base_kw))
            results.extend(site_ob.getCatalogedObjectsCheckView(meta_type=meta_list, path=path, address=query, **base_kw))
            
            if REQUEST:
                langs = REQUEST.get('languages', self.gl_get_selected_language())
            else:
                langs = self.gl_get_selected_language()
            langs = self.utConvertToList(langs)
            for lang in langs:
                kw = {'objectkeywords_%s' % (lang,) : query}
                kw.update(base_kw)
                #results.extend(site_ob.getCatalogedMapObjects(meta_type=meta_list, path=path, **kw))
                results.extend(site_ob.getCatalogedObjectsCheckView(meta_type=meta_list, path=path, **kw))

        #LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG, 'searchGeoPoints%s -> %s' % (
        #                repr((path, geo_types, query, REQUEST)),
        #                repr(results)))
        else:
            #results.extend(site_ob.getCatalogedMapObjects(meta_type=meta_list, path=path, **base_kw))
            results.extend(site_ob.getCatalogedObjectsCheckView(meta_type=meta_list, path=path, **base_kw))

        return self.utEliminateDuplicatesByURL(results)

    security.declareProtected(view, 'downloadLocationsKml')
    def downloadLocationsKml(self, path='', geo_types=None, geo_query='', REQUEST=None):
        """Returns the selected locations as a KML file"""
        path = path or '/'

        output = []
        out_app = output.append

        kml = kml_generator()
        out_app(kml.header())
        out_app(kml.style())
        for loc in self.searchGeoPoints(path, geo_types, geo_query):
            if loc.latitude is not None and loc.longitude is not None:
                out_app(kml.add_point(self.utToUtf8(loc.getId()),
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

    security.declareProtected(view, 'xrjs_getGeoPoints')
    def xrjs_getGeoPoints(self, REQUEST, path='', geo_types=None, geo_query=None):
        """ """
        r = []
        t = []
        ra = r.append
        portal_ob = self.getSite()
        if geo_types:
            for res in self.searchGeoPoints(path, geo_types, geo_query, REQUEST):
                try:
                    latitude = float(res.latitude);
                    longitude = float(res.longitude);
                except:
                    latitude = 0;
                    longitude = 0;

                if (latitude and longitude):
                    ra('%s##%s##mk_%s##%s##%s##%s$$' % (self.utToUtf8(res.latitude),
                                              self.utToUtf8(res.longitude),
                                              self.utToUtf8(res.id),
                                              self.utToUtf8(self.utJavaScriptEncode(res.title_or_id())),
                                              'mk_%s' % self.utToUtf8(res.geo_type),
                                              res.marker_html()
                                              ))

        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return ''.join(r)

    security.declareProtected(view, 'xrjs_simple_feed')
    def xrjs_simple_feed(self, key='', show='', REQUEST=None):
        """ """
        #if key == self.getSession(MSP_SESSION_KEY, None):
        res = ''
        ob = self.unrestrictedTraverse('%s' % show, None)
        if ob and not isinstance(ob, GeoMapTool):
            if ob.latitude is not None and ob.longitude is not None:
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
                out_a('mk_%s.size = new YSize(17, 17);' % symbol.id)
                out_a('mk_%s.offsetSmartWindow = new YCoordPoint(6, 11);' % symbol.id)
        return '\n'.join(output)


    def jsMarkerIcons(self):
        #load markers on the map
        output = []
        for symbol in self.getSymbolsList():
            icon_url = '%s/getSymbolPicture?id=%s' % (self.absolute_url(), symbol.id)
            output.append('"%s":"%s"' % (symbol.id, icon_url))
        return ",".join(output)
    
    def jsMapControl(self, map_engine="yahoo", center="", zoom="", width="", height="", enableKeyControls=False, map_types=[], default_type=""):
        """
        Load map control from ZPT template into web page
        """
        center_locality = center or self.center_locality
        center_zoom = zoom or self.center_zoom
        
        map_type = [];
        if "YAHOO_MAP_SAT" in map_types: map_type.append( "satellite" );
        if "YAHOO_MAP_REG" in map_types: map_type.append( "map" );
        if "YAHOO_MAP_HYB" in map_types: map_type.append( "hybrid" );

        initial_map_type = "map";
        if "YAHOO_MAP_SAT" == default_type: initial_map_type = "satellite";
        if "YAHOO_MAP_HYB" == default_type: initial_map_type = "hybrid";
                
        return get_template("map_loader.js") % (map_engine, 
                                                self.jsMarkerIcons(), #Marker icons types
                                                center, #Center location
                                                center_zoom, #Default zoom
                                                ("%s" % (enableKeyControls,)).lower(), #Enable mouse wheel zoom 
                                                "[%s];" % ",".join(["\"%s\"" % (k) for k in map_type]), #map types
                                                initial_map_type,
                                                self.absolute_url(),) #Absolute url for control


    #xmlrpc interface
    def xrjs_loader(self, show, geo_query, center='', zoom='', path='', width='', height='', enableKeyControls=True):
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
        strKeyControls = ""
        if not self.enableKeyControls or not enableKeyControls:
            strKeyControls = "map.disableKeyControls();"
        return get_template(TEMPLATE_XMLRPC_LOCATIONS_MAP_LOADER) % (center_locality, center_zoom, self.default_type, width, height, ",".join(self.map_types), strKeyControls, self.xrjs_markers(), self.absolute_url())

    def xrjs_simple_loader(self, show):
        #initialize marker loader - location
        xr_key = self.utGenRandomId(32)
        show = self.utJsEncode(show)
        self.setSession(MSP_SESSION_KEY, xr_key)
        ob = self.unrestrictedTraverse('%s' % show)
        center_locality, center_zoom = self.center_locality, self.center_zoom
        if ob:
            center_latitude, center_longitude = 0.0, 0.0
            if ob.latitude is not None and ob.longitude is not None:
                center_latitude, center_longitude, center_zoom = ob.latitude, ob.longitude, self.detailed_zoom
        return get_template(TEMPLATE_XMLRPC_SIMPLE_MAP_LOADER) % (center_latitude, center_longitude, center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types), self.get_location_marker(ob), self.absolute_url(), xr_key, show)

    def xrjs_editpick_loader(self, show):
        #initialize edit pick map
        show = self.utJsEncode(show)
        ob = self.unrestrictedTraverse('%s' % show)
        if ob:
            latitude, longitude, zoom = ob.latitude, ob.longitude, self.detailed_zoom
        return get_template(TEMPLATE_XMLRPC_EDITPICK_MAP_LOADER) % (latitude, longitude, zoom, self.center_locality, self.center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types))

    def xrjs_addpick_loader(self):
        #initialize add pick map
        center_locality, center_zoom = self.center_locality, self.center_zoom + 2
        return get_template(TEMPLATE_XMLRPC_ADDPICK_MAP_LOADER) % (center_locality, center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types))

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
        meta_type = 'Naaya GeoPoint'

        if latitude.strip() == '' and longitude.strip() == '':
            coordinates = location_geocode(address)
            if coordinates is None:
                LOG('NaayaCore.GeoMapTool.GeoMapTool.GeoMapTool', DEBUG, 'add_location: could not find coordinates for %s' % (address, ))
                latitude, longitude = None, None
            else:
                latitude, longitude = coordinates

        if meta_type in container.get_pluggable_installed_meta_types():
            try:
                ob = container.addNyGeoPoint(title=title, description=description, coverage='', keywords='', sortorder='', longitude=longitude, latitude=latitude, address=address, geo_type=geo_type, url=URL)
                ob.approveThis(approved)
                return (ob, None)
            except Exception, err:
                return (None, 'Failed to add %s geo-point! Error: %s' % (title, str(err)))

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'uploadLocations')
    def uploadLocations(self, file=None, dialect='comma', encoding='utf-8', approved=False, parent_folder='', geo_type='', REQUEST=None):
        """ """
        errs = []
        metadata = ['name', 'description', 'address', 'URL', 'latitude', 'longitude']


        try:
            if file:
                if file.filename.find('\\') != -1:
                    filename = file.filename.split('\\')[-1]
                else:
                    filename = file.filename
            else:
                raise GeoMapToolUploadError("No file uploaded.")

            #step 1. read the CSV file
            csv = CSVReader(file, dialect, encoding)
            records, error = csv.read()

            #validate metadata
            for meta in metadata:
                if meta not in records[0].keys():
                    raise GeoMapToolUploadError('Invalid headers in file.')

            #step 2. add locations
            if not parent_folder:
                raise GeoMapToolUploadError('The Upload in folder field must be an existing folder.')
            parent_ob = self.utGetObject(parent_folder)
            if not parent_ob:
                raise GeoMapToolUploadError('The Upload in folder field must be an existing folder.')

            num_nolocation = 0
            for rec in records:
                if not rec:
                    continue
                ob, err = self.add_location(self.utToUnicode(rec['name']),
                                            self.utToUnicode(rec['description']),
                                            rec['address'],
                                            rec.get('URL', ''),
                                            approved,
                                            parent_ob,
                                            geo_type,
                                            rec.get('latitude', ''),
                                            rec.get('longitude', ''))

                if err is not None:
                    errs.append(err)
                    continue
                if ob.longitude is None and ob.latitude is None:
                    num_nolocation += 1
        except GeoMapToolUploadError, ex:
            errs.append(str(ex)) # TODO Python 2.5: ex.message

        if errs:
            self.setSessionErrors(errs)
        else:
            self.setSessionInfo(["%u GeoPoint(s) uploaded. (%s)" % (len(records), self.utGetTodayDate())])
            if num_nolocation:
                self.setSessionErrors(["Could not geolocate %u address(es)." % (num_nolocation,)])
        return REQUEST.RESPONSE.redirect('%s/admin_mapupload_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getLocations')
    def getLocations(self, skey='', rkey=''):
        """ return the list of locations """
        locations = self.searchGeoPoints(approved=False)
        if skey in ['title', 'address', 'latitude', 'longitude']:
            locations = self.utSortObjsListByAttr(locations, skey, rkey)
        return locations

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getDuplicateLocations')
    def getDuplicateLocations(self, *args, **kw):
        """Returns a list of duplicate locations.

            It accepts the same the parameters as getLocations.
        """
        return list(findDuplicates(self.getLocations(*args, **kw), ('geo_type', 'address', 'longitude', 'latitude')))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteLocations')
    def deleteLocations(self, locations, REQUEST=None):
        """ delete locations """
        for location in locations:
            loc_obj = self.unrestrictedTraverse(location, None)
            if loc_obj:
                loc_obj.getParentNode().manage_delObjects([loc_obj.id])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminAddSymbol')
    def adminAddSymbol(self, title='', description='', parent='', picture='', sortorder='', REQUEST=None):
        """ """
        self.addSymbol('symbol%s' % self.utGenRandomId(3), title, description, parent, picture, sortorder)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminUpdateSymbol')
    def adminUpdateSymbol(self, id='', title='', description='', parent='', picture='', sortorder='', REQUEST=None):
        """ """
        self.updateSymbol(id, title, description, parent, picture, sortorder)
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
        if skey in ['title', 'parent', 'sortorder']:
            r = self.utSortObjsListByAttr(r, skey, rkey)
        return r



#########DESTINET#########

    security.declareProtected(view, 'downloadLocationsKml2')
    def downloadLocationsKml2(self, arrStakeholders='', arrSupplyChains='', arrAdministrativeLevels='', arrLandscapeTypes='', path='', geo_types=None, geo_query=None, REQUEST=None):
        """Returns the selected locations as a KML file"""
        path = path or '/'
        arr_geo_types = []
        if arrStakeholders:
            arr_geo_types.extend( arrStakeholders.split(',') );

        if arrSupplyChains:
            arr_geo_types.extend( arrSupplyChains.split(',') );

        landscape_types = []
        if arrLandscapeTypes:
            landscape_types  = arrLandscapeTypes.split(',');
        else:
            landscape_types = []

        administrative_levels = []
        if arrAdministrativeLevels:
            administrative_levels = arrAdministrativeLevels.split(',');
        else:
            administrative_levels = []

        output = []
        out_app = output.append

        kml = kml_generator()
        out_app(kml.header())
        out_app(kml.style())
        for loc in self.searchGeoPoints(path, arr_geo_types, geo_query, administrative_level=administrative_levels, landscape_type=landscape_types):
            if loc.latitude is not None and loc.longitude is not None:
                out_app(kml.add_point(self.utToUtf8(loc.getId()),
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

    security.declareProtected(view, 'search_geopoints_frontpage')
    def search_geopoints_frontpage(self, arrStakeholders='', arrSupplyChains='', arrAdministrativeLevels='', arrLandscapeTypes='', path='', geo_types=None, geo_query=None, REQUEST=None):
        """ """
        arr_geo_types = []
        if arrStakeholders:
            arr_geo_types.extend( arrStakeholders.split(',') );

        if arrSupplyChains:
            arr_geo_types.extend( arrSupplyChains.split(',') );

        landscape_types = []
        if arrLandscapeTypes:
            landscape_types  = arrLandscapeTypes.split(',');
        else:
            landscape_types = []

        administrative_levels = []
        if arrAdministrativeLevels:
            administrative_levels = arrAdministrativeLevels.split(',');
        else:
            administrative_levels = []

        r = []
        ra = r.append
        portal_ob = self.getSite()
        if arr_geo_types:
            arr = self.searchGeoPoints(path, arr_geo_types, geo_query, administrative_level=administrative_levels, landscape_type=landscape_types);
            for res in arr:
                try:
                    latitude = float(res.latitude);
                    longitude = float(res.longitude);
                except:
                    latitude = 0;
                    longitude = 0;

                if (latitude and longitude):
                    ra('%s##%s##mk_%s##%s##%s##%s$$' % (self.utToUtf8(res.latitude),
                                              self.utToUtf8(res.longitude),
                                              self.utToUtf8(res.id),
                                              self.utToUtf8(self.utJavaScriptEncode(res.title_or_id())),
                                              'mk_%s' % self.utToUtf8(res.geo_type),
                                              res.marker_html()
                                              ))

        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return ''.join(r)



    def create_xml_for_tabs(self, symbols_list=None):
        if symbols_list is not None and len(symbols_list) > 0:
            r = []
            for symbol in symbols_list:
                s = """ <item text="%s" id="%s" im0="%s" im1="folderOpen.gif" im2="folderClosed.gif" />""" \
                  % (self.utXmlEncode(symbol.title), self.utXmlEncode(symbol.id), 'portal_map/getSymbolPicture?id=%s' % ( symbol.id ) )
                r.append(s)

            self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
            return """<?xml version="1.0" encoding="utf-8"?>
            <tree id="0">
                <item text="All" id="cat_all" open="1" im0="tombs.gif" im1="tombs.gif" im2="iconSafe.gif" call="1" select="1">
                %s
                </item>
            </tree>
            """ % ''.join(r)

    def get_stakeholders_xml(self):
        """ """
        parents = self.getParentsList()
        if parents and len( parents ) > 1:
            return self.create_xml_for_tabs( self.getSymbolChildren(parents[0].id) );
        return """<?xml version="1.0" encoding="utf-8"?><tree id="0"></tree>"""


    def get_supplyChain_xml(self):
        """ """
        parents = self.getParentsList()
        if parents and len( parents ) > 1:
            return self.create_xml_for_tabs( self.getSymbolChildren(parents[1].id) );
        return """<?xml version="1.0" encoding="utf-8"?><tree id="0"></tree>"""


    def get_administrative_xml(self):
        """ """
        adminlist = self.getPortletsTool().getRefListById('administrative_level').get_list()
        return self.create_xml_for_tabs( adminlist );


    def get_landscape_xml(self):
        """ """
        adminlist = self.getPortletsTool().getRefListById('landscape_type').get_list()
        return self.create_xml_for_tabs( adminlist );


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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_mapduplicatelocations_html')
    admin_mapduplicatelocations_html = PageTemplateFile('zpt/map_duplicate_locations', globals())

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
