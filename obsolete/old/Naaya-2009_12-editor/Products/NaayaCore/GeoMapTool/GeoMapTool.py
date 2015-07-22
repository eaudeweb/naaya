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
#David Batranu (Eau de Web) added support for multiple domains
#Andrei Laza (Eau de Web) refactored search and added clusters

#Python imports
import os.path
from decimal import Decimal
from datetime import datetime
import time
from xml.dom import minidom
import simplejson as json

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from zLOG import LOG, DEBUG, INFO, ERROR
from App.ImageFile import ImageFile

#Product imports
from constants import *
from Products.NaayaBase.constants import *
import Products.NaayaBase.NyContentType
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils, findDuplicates
from Products.NaayaCore.managers.session_manager import session_manager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.GeoMapTool import clusters
from Products.NaayaCore.GeoMapTool import clusters_catalog

from managers.symbols_tool import symbols_tool
from managers.kml_gen import kml_generator
from managers.kml_parser import parse_kml
from managers.csv_reader import CSVReader
from managers.geocoding import location_geocode
from managers.yahoo import Yahoo

def get_template(name, skip_script=False):
    f = open(os.path.join(os.path.dirname(__file__), 'templates', name))
    try:
        content = f.read()
    finally:
        f.close()
    if skip_script:
        return content
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
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class GeoMapTool(Folder, utils, session_manager, symbols_tool):
    """
    Class that implements the tool.
    """

    mapsapikey = ['m.6kzBLV34FOaYaMCfIKBRHIIYE8zCf6c6yxcc5rZCWkCilWFPzAhcyQEcRTgYKy5g--']
    googleApiKey = ['ABQIAAAAkblOrSS9iVzkKUfXj3gOFRR26BjrSmLtamIPMRgDuTUxZh8BLxQ2qfb6PUeks1ZMeSmUGC0ZTrNFVg']
    map_engine = 'yahoo'
    #center map in Europe
    center_locality = MAP_CENTER_LOCALITY
    center_zoom = MAP_CENTER_ZOOM
    detailed_zoom = MAP_DETAILED_ZOOM
    map_width = MAP_WIDTH
    map_height = MAP_HEIGHT
    detailed_map_width = MAP_DETAILED_WIDTH
    detailed_map_height = MAP_DETAILED_HEIGHT
    map_types = YAHOO_MAP_TYPES
    default_type = 'YAHOO_MAP_REG'
    enableKeyControls = True
    _cluster_pngs = [ImageFile('images/cluster_less_10.png', globals()),
                        ImageFile('images/cluster_10_100.png', globals()),
                        ImageFile('images/cluster_100_1k.png', globals()),
                        ImageFile('images/cluster_1k_more.png', globals())]
    def _pick_cluster(self, len_group):
        if len_group > 1000:
            return 3
        elif len_group > 100:
            return 2
        elif len_group > 10:
            return 1
        else:
            return 0

    _marker_template = """
        <div class="marker-body">
            <h3>%s</h3>
            %s
            <small>%s</small>
            <div class="marker-more">
                <a href="%s" i18n:translate="">see more</a>
            </div>
        </div>
        """

    _small_marker_template = """
        <div class="marker-more">
            <a href="%s" i18n:translate="">%s</a>%s
        </div>
        """

    def get_small_marker(self, object):
        has_access = bool(self.REQUEST.AUTHENTICATED_USER.has_permission(permission=view,
                                                                        object=object))
        access_str = ''
        if not has_access:
            access_str = '(RESTRICTED ACCESS)'
        return self._small_marker_template % (object.absolute_url(),
                                            object.title_or_id(),
                                            access_str)

    def get_marker(self, object):
        has_access = bool(self.REQUEST.AUTHENTICATED_USER.has_permission(permission=view,
                                                                        object=object))
        access_str = ''
        if not has_access:
            access_str = '<div>RESTRICTED ACCESS</div>'
        return self._marker_template % (object.title_or_id(),
                                        access_str,
                                        object.description,
                                        object.absolute_url())

    _cluster_marker_template = """
        <div class="marker-body">
            <h3>Cluster</h3>
            <small>%s location(s) inside</small>
        </div>
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
        self.mapsapikey = ['m.6kzBLV34FOaYaMCfIKBRHIIYE8zCf6c6yxcc5rZCWkCilWFPzAhcyQEcRTgYKy5g--']
        self.googleApiKey = ['ABQIAAAAkblOrSS9iVzkKUfXj3gOFRR26BjrSmLtamIPMRgDuTUxZh8BLxQ2qfb6PUeks1ZMeSmUGC0ZTrNFVg']
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
    def manageProperties(self, mapsapikey=[], googleApiKey=[], map_engine='', center_locality='', center_zoom='', detailed_zoom='', map_width='', map_height='', detailed_map_width='', detailed_map_height='', map_types=[], default_type='', enableKeyControls='', REQUEST=None):
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

    def get_mapsapikey(self):
        """Return the Yahoo API key for the current domain"""
        yahoo_key = self.mapsapikey
        current_domain = getattr(self.REQUEST, 'other')['SERVER_URL']
        if isinstance(yahoo_key, list):                 #backwards compatibility
            keys = []
            #split the domain/key pairs
            for domain_key in yahoo_key:
                key_mapping = tuple(domain_key.split('::'))
                #only add keys that specify a domain
                if len(key_mapping) == 2:
                    keys.append(key_mapping)
            if keys:
                for domain, key in keys:
                    if domain == current_domain:
                        return key
            #no domain/key pairs were found, return the first value in the list
            if len(yahoo_key):
                return yahoo_key[0]
            return ''
        return yahoo_key

    def display_mapsapikeys(self):
        key = self.mapsapikey
        if isinstance(key, list):
            return '\n'.join(key)
        else:
            return self.mapsapikey

    def get_googleApiKey(self):
        """Return the Google API key for the current domain"""
        google_key = self.googleApiKey
        current_domain = getattr(self.REQUEST, 'other')['SERVER_URL']
        if isinstance(google_key, list):                #backwards compatibility
            keys = []
            #split the domain/key pairs
            for domain_key in google_key:
                key_mapping = tuple(domain_key.split('::'))
                #only add keys that specify a domain
                if len(key_mapping) == 2:
                    keys.append(key_mapping)
            if keys:
                for domain, key in keys:
                    if domain == current_domain:
                        return key
            #no domain/key pairs were found, return the first value in the list
            if len(google_key):
                return google_key[0]
            return ''
        return google_key

    def display_googleApiKeys(self):
        key = self.googleApiKey
        if isinstance(key, list):
            return '\n'.join(key)
        else:
            return key

    def can_filter_by_first_letter(self):
        catalog_tool = self.getCatalogTool()
        return catalog_tool._catalog.indexes.has_key('full_title')

    security.declarePrivate('build_geo_filters')
    def build_geo_filters(self, path='', meta_types=None, geo_types=None,
            approved=True,
            landscape_type=[], administrative_level=[],
            lat_min=-90., lat_max=90., lon_min=-180., lon_max=180.,
            query='', languages=None, first_letter=None):
        base_filter = {}

        base_filter['path'] = path

        if meta_types is None:
            base_filter['meta_type'] = self.get_geotaggable_meta_types()
        else:
            base_filter['meta_type'] = meta_types

        if geo_types is not None:
            base_filter['geo_type'] = geo_types

        if approved:
            base_filter['approved'] = 1

        if landscape_type:
            base_filter['landscape_type'] = landscape_type

        if administrative_level:
            base_filter['administrative_level'] = administrative_level

        base_filter['geo_latitude'] = {'query': (Decimal(str(lat_min)), Decimal(str(lat_max))),
                                        'range':'min:max'}
        base_filter['geo_longitude'] = {'query': (Decimal(str(lon_min)), Decimal(str(lon_max))),
                                        'range':'min:max'}

        filters = []
        filters.append(base_filter)

        if query:
            query_filters = []
            for f in filters:
                f_full_text = f.copy()
                f_full_text['PrincipiaSearchSource'] = query
                query_filters.append(f_full_text)

                if languages == None:
                    languages = self.gl_get_selected_language()
                languages = self.utConvertToList(languages)
                for lang in languages:
                    f_keywords = f.copy()
                    f_keywords['objectkeywords_%s' % (lang,)] = query
                    query_filters.append(f_keywords)
            filters = query_filters

        if first_letter:
            letter_filters = []
            for f in filters:
                f_lower = f.copy()
                f_lower['full_title'] = {'query': (first_letter.upper(), chr(ord(first_letter.upper())+1)),
                                            'range':'min:max'}
                letter_filters.append(f_lower)

                f_upper = f.copy()
                f_upper['full_title'] = {'query': (first_letter.lower(), chr(ord(first_letter.lower())+1)),
                                            'range':'min:max'}
                letter_filters.append(f_upper)
            filters = letter_filters

        return filters

    security.declarePrivate('get_geo_objects')
    def get_geo_objects(self, lat, lon, path='', geo_types=None, query='',
            approved=True, landscape_type=[], administrative_level=[], languages=None):
        """ """
        catalog_tool = self.getCatalogTool()

        eps = Decimal('0.000001')
        lat, lon = Decimal(lat), Decimal(lon)
        filters = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat-eps, lat_max=lat+eps, lon_min=lon-eps, lon_max=lon+eps,
                query=query, languages=languages)

        # OR the filters
        brains = []
        for f in filters:
            brains.extend(catalog_tool(f))

        # getting the unique data record ids
        dict_rids = {}
        rids = []
        for b in brains:
            rid = b.data_record_id_
            if rid not in dict_rids:
                dict_rids[rid] = 1
                rids.append(rid)

        results = map(lambda rid: catalog_tool.getobject(rid), rids)
        return results

    security.declarePrivate('_search_geo_objects')
    def _search_geo_objects(self, filters, sort_on, sort_order):
        """
        Returns all the objects that match the specified criteria.
        This does not check for the 180/-180 meridian in the map
        """
        catalog_tool = self.getCatalogTool()

        brains = []
        for f in filters:
            brains.extend(catalog_tool(f))

        # getting the unique data record ids
        dict_rids = {}
        rids = []
        for b in brains:
            rid = b.data_record_id_
            if rid not in dict_rids:
                dict_rids[rid] = 1
                rids.append(rid)

        results = map(lambda rid: catalog_tool.getobject(rid), rids)

        # manual sorting
        key_func = None
        if sort_on == 'title':
            key_func = lambda x: x.title
        elif sort_on == 'geo_address':
            key_func = lambda x: x.geo_location.address
        elif sort_on == 'geo_latitude':
            key_func = lambda x: x.geo_location.lat
        elif sort_on == 'geo_longitude':
            key_func = lambda x: x.geo_location.lon

        reverse = (sort_order == 'reverse')

        if key_func is not None:
            results.sort(key=key_func, reverse=reverse)

        return results

    security.declareProtected(view, 'search_geo_objects')
    def search_geo_objects(self, lat_min=None, lat_max=None, lon_min=None, lon_max=None,
            path='', geo_types=None, query='', approved=True, lat_center=None, lon_center=None,
            landscape_type=[], administrative_level=[], languages=None, first_letter=None,
            sort_on='', sort_order=''):
        """ Returns all the objects that match the specified criteria.

                lat_min -- string/float: minimum latitude for results
                lat_max -- string/float: maximum latitude for results
                lon_min -- string/float: minimum longitude for results
                lon_max -- string/float: maximum longitude for results
                path -- string: where to search
                qeo_types -- list: types to search (if None all geo types are searched)
                query -- string: text searched in the full text search
                approved -- bool: if True return only approved items, otherwise return all items
                languages -- list:
                first_letter -- char: The first letter in the title
                sort_on -- string: what index to sort on
                sort_order -- string: if empty then normal order; if 'reverse' then reversed order
        """
        if lat_min is None or lat_min == '': lat_min = -90.
        if lat_max is None or lat_max == '': lat_max = 90.
        if lon_min is None or lon_min == '': lon_min = -180.
        if lon_max is None or lon_max == '': lon_max = 180.
        if lat_center is None or lat_center == '': lat_center = 0.
        if lon_center is None or lon_center == '': lon_center = 0.

        if float(lon_min) > float(lon_max):
            lon_min, lon_max = lon_max, lon_min

        if float(lon_min) < float(lon_center) < float(lon_max):
            filters = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max,
                query=query, languages=languages, first_letter=first_letter)

        else:
            filters = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat_min, lat_max=lat_max, lon_min=lon_max, lon_max=180.,
                query=query, languages=languages, first_letter=first_letter)

            filters2 = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat_min, lat_max=lat_max, lon_min=-180., lon_max=lon_min,
                query=query, languages=languages, first_letter=first_letter)

            filters.extend(filters2)

        results = self._search_geo_objects(filters, sort_on, sort_order)
        return results

    security.declarePrivate('_search_geo_clusters')
    def _search_geo_clusters(self, filters):
        """
        Returns all the clusters that match the specified criteria.
        This does not check for the 180/-180 meridian in the map
        """
        # unpack map limits
        if filters:
            lat_min = float(filters[0]['geo_latitude']['query'][0])
            lat_max = float(filters[0]['geo_latitude']['query'][1])

            lon_min = float(filters[0]['geo_longitude']['query'][0])
            lon_max = float(filters[0]['geo_longitude']['query'][1])
        else: # this should not happen
            return [], []

        #preparing for the call to the catalog
        catalog_tool = self.getCatalogTool()

        # call the improved cluster_catalog function for getting the clusters
        centers, groups = clusters_catalog.getClusters(catalog_tool, filters)

        # transform centers to Geo
        centers = map(lambda c: Geo(str(c.lat), str(c.lon)), centers)

        cluster_obs, single_obs = [], []
        for i in range(len(centers)):
            if len(groups[i]) < 10: # from this const on we actually return clusters
                for so in groups[i]:
                    sobject = clusters_catalog.getObjectFromCatalog(catalog_tool, so)

                    # do not display it if it is not in the actual map
                    if Decimal(str(lat_min)) < sobject.geo_location.lat < Decimal(str(lat_max)):
                        if Decimal(str(lon_min)) < sobject.geo_location.lon < Decimal(str(lon_max)):
                            single_obs.append(sobject)
            else:
                if Decimal(str(lat_min)) < centers[i].lat < Decimal(str(lat_max)):
                        if Decimal(str(lon_min)) < centers[i].lon < Decimal(str(lon_max)):
                            cluster_obs.append((centers[i], len(groups[i])))

        return cluster_obs, single_obs

    security.declareProtected(view, 'search_geo_clusters')
    def search_geo_clusters(self, lat_min=None, lat_max=None, lon_min=None, lon_max=None, zoom_level=None,
            path='', geo_types=None, query='', approved=True, lat_center=None, lon_center=None,
            landscape_type=[], administrative_level=[], languages=None):
        """ Returns all the clusters that match the specified criteria. """
        if zoom_level is None: zoom_level = 0
        if lat_min is None or lat_min == '': lat_min = -90.
        if lat_max is None or lat_max == '': lat_max = 90.
        if lon_min is None or lon_min == '': lon_min = -180.
        if lon_max is None or lon_max == '': lon_max = 180.
        if lat_center is None or lat_center == '': lat_center = 0.
        if lon_center is None or lon_center == '': lon_center = 0.
        zoom_level = int(zoom_level)
        lat_min, lat_max = float(lat_min), float(lat_max)
        lon_min, lon_max = float(lon_min), float(lon_max)
        lat_center, lon_center = float(lat_center), float(lon_center)

        # check for the 180/-180 longitude in the map
        if float(lon_min) > float(lon_max):
            lon_min, lon_max = lon_max, lon_min

        if float(lon_min) < float(lon_center) < float(lon_max):
            filters = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max,
                query=query, languages=languages)

        else:
            filters = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat_min, lat_max=lat_max, lon_min=lon_max, lon_max=180.,
                query=query, languages=languages)

            filters2 = self.build_geo_filters(path=path, geo_types=geo_types,
                approved=approved,
                landscape_type=landscape_type, administrative_level=administrative_level,
                lat_min=lat_min, lat_max=lat_max, lon_min=-180., lon_max=lon_min,
                query=query, languages=languages)

            filters.extend(filters2)

        cluster_obs, single_obs = self._search_geo_clusters(filters)
        return cluster_obs, single_obs

    security.declareProtected(view, 'downloadLocationsKml')
    def downloadLocationsKml(self, path='', geo_types=None, geo_query='', REQUEST=None):
        """Returns the selected locations as a KML file"""
        path = path or '/'

        output = []
        out_app = output.append

        kml = kml_generator()
        out_app(kml.header())
        out_app(kml.style())
        for loc in self.search_geo_objects(path=path, geo_types=geo_types, query=geo_query):
            if loc.geo_location is not None:
                try:
                    loc_url = loc.url
                except AttributeError:
                    loc_url = ''

                out_app(kml.add_point(self.utToUtf8(loc.getId()),
                                      self.utXmlEncode(loc.title_or_id()),
                                      self.utXmlEncode(loc.description),
                                      '%s/getSymbolPicture?id=%s' % (self.absolute_url(), self.utToUtf8(loc.geo_type)),
                                      self.utToUtf8(loc.geo_location.lon),
                                      self.utToUtf8(loc.geo_location.lat),
                                      self.utXmlEncode(self.getSymbolTitle(loc.geo_type)),
                                      self.utToUtf8(self.absolute_url()),
                                      self.utToUtf8(loc.absolute_url()),
                                      self.utToUtf8(loc_url),
                                      self.utXmlEncode(loc.geo_location.address)))
        out_app(kml.footer())
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/vnd.google-earth.kml+xml')
        REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=locations.kml')
        return '\n'.join(output)

    security.declareProtected(view, 'xrjs_getZoomLevel')
    def xrjs_getZoomLevel(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        address = kwargs.get('address', '')
        if not address:
            return 6
        return Yahoo(self.get_mapsapikey()).get_zoom_level(address)

    security.declareProtected(view, 'xrjs_getGeoPoints')
    def xrjs_getGeoPoints(self, REQUEST, path='', geo_types=None, geo_query=None, lat_min=-90., lat_max=90., lon_min=-180., lon_max=180.):
        """ """
        r = []
        t = []
        ra = r.append
        portal_ob = self.getSite()
        if geo_types:
            filters = self.build_geo_filters(path=path, geo_types=geo_types, query=geo_query, lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max)
            for res in self._search_geo_objects(filters):
                if res.geo_location is not None:
                    ra('%s##%s##mk_%s##%s##%s##%s' % (self.utToUtf8(res.geo_location.lat),
                                              self.utToUtf8(res.geo_location.lon),
                                              self.utToUtf8(res.id),
                                              self.utToUtf8(self.utJavaScriptEncode(res.title_or_id())),
                                              'mk_%s' % self.utToUtf8(res.geo_type),
                                              self.utToUtf8(self.get_marker(res)),
                                              ))

        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return '$$'.join(r)

    security.declareProtected(view, 'xrjs_getGeoClusters')
    def xrjs_getGeoClusters(self, REQUEST, path='', geo_types=None, geo_query=None,
            zoom_level=0, lat_min=-90., lat_max=90., lon_min=-180., lon_max=180.,
            lat_center=0., lon_center=0.):
        """ """
        r = []
        cluster_obs, single_obs = self.search_geo_clusters(path=path, geo_types=geo_types, query=geo_query,
                              zoom_level=zoom_level, lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max,
                              lat_center=lat_center, lon_center=lon_center)

        for res in cluster_obs:
            r.append('%s##%s##mk_%s##%s##%s##%s' % (self.utToUtf8(res[0].lat),
                                              self.utToUtf8(res[0].lon),
                                              '', # id
                                              'cluster', # title or id
                                              'mk_cluster_%s' % self._pick_cluster(res[1]), # geo_type
                                               self.utToUtf8(self._cluster_marker_template % res[1]), # tooltip
                                              ))
        for res in single_obs:
            r.append('%s##%s##mk_%s##%s##%s##%s' % (self.utToUtf8(res.geo_location.lat),
                                              self.utToUtf8(res.geo_location.lon),
                                              self.utToUtf8(res.id),
                                              self.utToUtf8(self.utJavaScriptEncode(res.title_or_id())),
                                              'mk_%s' % self.utToUtf8(res.geo_type),
                                              self.utToUtf8(self.get_marker(res)),
                                              ))

        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return '$$'.join(r)


    security.declareProtected(view, 'xrjs_getTooltip')
    def xrjs_getTooltip(self, lat, lon, path='', geo_types=None, geo_query=None):
        """ """
        obs = self.get_geo_objects(lat, lon, path, geo_types, geo_query)
        if len(obs) == 1:
            return self.utToUtf8(self.get_marker(obs[0]))

        ret = ''
        for ob in obs:
            ret += self.get_small_marker(ob)
        return ret

    security.declareProtected(view, 'xrjs_simple_feed')
    def xrjs_simple_feed(self, key='', show='', REQUEST=None):
        """ """
        #if key == self.getSession(MSP_SESSION_KEY, None):
        res = ''
        ob = self.unrestrictedTraverse('%s' % show, None)
        if ob and not isinstance(ob, GeoMapTool):
            if ob.geo_location is not None:
                res = '%s|%s|%s' % (ob.geo_location.lat, ob.geo_location.lon, self.utJavaScriptEncode(ob.title_or_id()))
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

        for i in range(len(self._cluster_pngs)):
            icon_url = '%s/getSymbolPicture?id=symbol_cluster_%s' % (self.absolute_url(), i)
            output.append('"cluster_%s": "%s"' % (i, icon_url))
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
            if ob.geo_location is not None:
                center_latitude, center_longitude, center_zoom = ob.geo_location.lat, ob.geo_location.lon, self.detailed_zoom
        return get_template(TEMPLATE_XMLRPC_SIMPLE_MAP_LOADER) % (center_latitude, center_longitude, center_zoom, self.default_type, self.detailed_map_width, self.detailed_map_height, ",".join(self.map_types), self.get_location_marker(ob), self.absolute_url(), xr_key, show)

    def xrjs_editpick_loader(self, show):
        #initialize edit pick map
        show = self.utJsEncode(show)
        ob = self.unrestrictedTraverse('%s' % show)
        if not ob or ob.geo_location is None:
            return None
        latitude, longitude, zoom = ob.geo_location.lat, ob.geo_location.lon, self.detailed_zoom
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
                ob_id = container.addNyGeoPoint(title=title, description=description, longitude=longitude, latitude=latitude, address=address, geo_type=geo_type, url=URL)
                ob = container._getOb(ob_id)
                ob.approveThis(approved)
                self.recatalogNyObject(ob)
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

            if dialect != 'kml':
                #step 1. read the CSV file
                csv = CSVReader(file, dialect, encoding)
                records, error = csv.read()

                #validate metadata
                for meta in metadata:
                    if meta not in records[0].keys():
                        raise GeoMapToolUploadError('Invalid headers in file.')
            else:
                records = parse_kml(file)

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
                                            rec.get('address', ''),
                                            rec.get('URL', ''),
                                            approved,
                                            parent_ob,
                                            geo_type,
                                            rec.get('latitude', ''),
                                            rec.get('longitude', ''))

                if err is not None:
                    errs.append(err)
                    continue
                if ob.geo_location is not None:
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
        locations = self.search_geo_objects(approved=False)
        if skey in ['title', 'address', 'latitude', 'longitude']:
            locations = self.utSortObjsListByAttr(locations, skey, rkey)
        return locations

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getDuplicateLocations')
    def getDuplicateLocations(self, criteria, sort_on="", sort_order=""):
        """Returns a list of duplicate locations.

            It accepts the same the parameters as getLocations.
        """
        all_items = {}
        objects = self.search_geo_objects(sort_on=sort_on, sort_order=sort_order)

        for i in range(len(objects)):
            item = objects[i]
            marker = []
            if 'type' in criteria:
                marker.append(item.geo_type)
            if 'latlon' in criteria:
                marker.append(item.geo_location.lat)
                marker.append(item.geo_location.lon)
            if 'address' in criteria:
                marker.append(item.geo_location.address)
            if 'title' in criteria:
                marker.append(item.title_or_id())
            all_items.setdefault(tuple(marker), []).append((item, i))

        ret = []
        for items in all_items.values():
            if len(items) < 2:
                continue
            for item in items:
                ret.append(item)

        ret.sort(key=lambda x: x[1])
        ret = [x[0] for x in ret]
        return ret

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getNoCoordinatesObjects')
    def getNoCoordinatesObjects(self, *args, **kw):
        """Returns a list of objects with no coordinates

            It accepts the same the parameters as getLocations.
        """
        ret = []
        catalog_tool = self.getCatalogTool()
        meta_types = self.get_geotaggable_meta_types()
        schema_tool = self.getSite().portal_schemas

        objects = []
        for b in catalog_tool():
            try:
                objects.append(catalog_tool.getobject(b.getRID()))
            except KeyError:
                pass

        for item in objects:
            if isinstance(item, Products.NaayaBase.NyContentType.NyContentType):
                schema = schema_tool.getSchemaForMetatype(item.meta_type)
                if schema is None:
                    continue

                if not 'geo_location-property' in schema.objectIds():
                    continue
                if not 'geo_location' in (schema.getDefaultDefinition() or {}):
                    continue

                if item.meta_type not in meta_types:
                    continue

                first_letter = kw['first_letter']
                if first_letter:
                    if not item.title.upper().startswith(first_letter.upper()):
                        continue

                if (item.geo_type is None) or (item.geo_type == ''):
                    ret.append(item)
                elif (item.geo_location is None):
                    ret.append(item)
                elif (item.geo_location.lat is None) or (item.geo_location.lon is None):
                    ret.append(item)
        return ret

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteLocations')
    def deleteLocations(self, locations, REQUEST=None):
        """ delete locations """
        for location in locations:
            loc_obj = self.unrestrictedTraverse(location, None)
            if loc_obj:
                loc_obj.getParentNode().manage_delObjects([loc_obj.getId()])
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
        for loc in self.search_geo_objects(path=path, geo_types=arr_geo_types, query=geo_query, administrative_level=administrative_levels, landscape_type=landscape_types):
            if loc.geo_location is not None:
                out_app(kml.add_point(self.utToUtf8(loc.getId()),
                                      self.utXmlEncode(loc.title),
                                      self.utXmlEncode(loc.description),
                                      '%s/getSymbolPicture?id=%s' % (self.absolute_url(), self.utToUtf8(loc.geo_type)),
                                      self.utToUtf8(loc.geo_location.lon),
                                      self.utToUtf8(loc.geo_location.lat),
                                      self.utXmlEncode(self.getSymbolTitle(loc.geo_type)),
                                      self.utToUtf8(self.absolute_url()),
                                      self.utToUtf8(loc.absolute_url()),
                                      self.utToUtf8(loc.url),
                                      self.utXmlEncode(loc.geo_location.address)))
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
            arr = self.search_geo_objects(path=path, geo_types=arr_geo_types, query=geo_query, administrative_level=administrative_levels, landscape_type=landscape_types);
            for res in arr:
                if res.geo_location is not None:
                    ra('%s##%s##mk_%s##%s##%s##%s' % (self.utToUtf8(res.geo_location.lat),
                                              self.utToUtf8(res.geo_location.lon),
                                              self.utToUtf8(res.id),
                                              self.utToUtf8(self.utJavaScriptEncode(res.title_or_id())),
                                              'mk_%s' % self.utToUtf8(res.geo_type),
                                              self.utToUtf8(self._marker_template % (res.title_or_id(),
                                                res.description, res.absolute_url()))
                                              ))

        REQUEST.RESPONSE.setHeader('Content-type', 'text/html;charset=utf-8')
        return '$$'.join(r)



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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_set_contenttypes')
    def admin_set_contenttypes(self, geotag=[], REQUEST=None):
        """ Configure which content types are geotaggable """

        for schema in self.getSite().portal_schemas.objectValues():
            new_visible = (schema.id in geotag)
            schema.getWidget('geo_location').visible = new_visible
            schema.getWidget('geo_type').visible = new_visible

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_map_contenttypes_html')


    def list_geotaggable_types(self):
        portal_schemas = self.getSite().portal_schemas
        output = []
        for schema in portal_schemas.listSchemas(installed=True).values():
            try:
                geo_location = schema.getWidget('geo_location');
                geo_type = schema.getWidget('geo_type');
            except KeyError:
                # one or both widgets are missing; skip it
                continue
            output.append({'id': schema.id, 'title': schema.title_or_id(),
                'enabled': geo_location.visible and geo_type.visible})
        return output

    def is_geotaggable(self, ob):
        geotaggable_types = [x['id'] for x in self.list_geotaggable_types() if x['enabled']]
        return ob.__class__.__name__ in geotaggable_types

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if hasattr(self, 'map_index'):
            return self._getOb('map_index')({'here': self})
        for skel_handler in reversed(self.get_all_skel_handlers()):
            skel_path = skel_handler.skel_path
            map_index_path = os.path.join(skel_path, 'others', 'map_index.zpt')
            if os.path.isfile(map_index_path):
                return PageTemplateFile(map_index_path).__of__(self)()
            break # we're only interested in the skel for the current portal type
        return self.view_map_html({'here': self})

    security.declareProtected(view, 'view_map_html')
    view_map_html = PageTemplateFile('zpt/map_index', globals())

    security.declareProtected(view, 'embed_map_html')
    embed_map_html = PageTemplateFile('zpt/map_embed', globals())

    security.declareProtected(view, 'list_locations')
    def list_locations(self, REQUEST=None, **kw):
        """" """
        if REQUEST is not None:
            kw.update(REQUEST.form)
        lat_min, lat_max, lon_min, lon_max = \
               kw.get('lat_min', ''),\
               kw.get('lat_max', ''),\
               kw.get('lon_min', ''),\
               kw.get('lon_max', '')
        lat_center, lon_center = \
                kw.get('lat_center', ''),\
                kw.get('lon_center', '')
        geo_types = kw.get('geo_types', '')
        if isinstance(geo_types, str):
            geo_types = geo_types.split(',')
        geo_query = kw.get('geo_query', '')

        sort_on, sort_order = '', ''
        if kw.get('sortable', ''):
            sort_on = kw.get('sort_on', '') 
            sort_order = kw.get('sort_order', '')

        first_letter = kw.get('first_letter', '')

        results = self.search_geo_objects(
            lat_min=lat_min, lat_max=lat_max, lon_min=lon_min,
            lon_max=lon_max, geo_types=geo_types, query=geo_query,
            first_letter=first_letter, sort_on=sort_on, sort_order=sort_order,
            lat_center=lat_center, lon_center=lon_center,
        )

        options = {}
        options['lat_min'] = lat_min
        options['lat_max'] = lat_max
        options['lon_min'] = lon_min
        options['lon_max'] = lon_max
        options['lat_center'] = lat_center
        options['lon_center'] = lon_center
        options['symbols'] = ','.join(geo_types)
        options['geo_types'] = geo_types
        options['geo_query'] = geo_query
        options['step'] = int(kw.get('step', '50'))
        step = options['step']
        options['start'] = int(kw.get('start', '0'))
        options['end'] = int(kw.get('end', step))
        options['sortable'] = kw.get('sortable', 'True')
        options['sort_on'] = sort_on
        options['sort_order'] = sort_order
        options['first_letter'] = first_letter
        options['results'] = len(results)
        options['next_start'] = options['end']
        options['next_end'] = options['end'] + step
        options['prev_start'] = options['start'] - step
        options['prev_end'] = options['start']
        options['records'] = results[options['start']:options['end']]
        return PageTemplateFile('zpt/list_locations',  globals()).__of__(self)(**options)

    security.declareProtected(view, 'export_geo_rss')
    def export_geo_rss(self, lat_min=None, lat_max=None, lon_min=None, lon_max=None,
            path='', geo_types=None, geo_query='', approved=True, lat_center=None, lon_center=None,
            landscape_type=[], administrative_level=[], languages=None,
            sort_on='', sort_order='', REQUEST=None):
        """ """
        if isinstance(geo_types, str):
            geo_types = geo_types.split(',')
        timestamp = datetime.fromtimestamp(time.time())
        timestamp = str(timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        rss = ["""<feed xmlns="http://www.w3.org/2005/Atom" xmlns:georss="http://www.georss.org/georss">
              <title>%s</title>
              <id>%s</id>
              <link rel="self" href="%s" />
              <author><name>European Environment Agency</name></author>
              <updated>%s</updated>
              """ % (self.title, self.absolute_url(), self.absolute_url(), timestamp) ]
        items = self.search_geo_objects(lat_min, lat_max, lon_min, lon_max,
                                        path, geo_types, geo_query, approved, lat_center, lon_center,
                                        landscape_type, administrative_level, languages,
                                        sort_on, sort_order)
        for item in items:
            doc = minidom.Document()
            entry = doc.createElement("entry")

            id_node = doc.createElement("id")
            id_node.appendChild(doc.createTextNode("%s" % (item.absolute_url(1))))
            entry.appendChild(id_node)

            link_node = doc.createElement("link")
            link_node.setAttribute("href", item.absolute_url())
            entry.appendChild(link_node)

            title_node = doc.createElement("title")
            if item.title:
                title = doc.createTextNode(item.title.encode('utf-8').decode('utf-8'))
            else:
                title = doc.createTextNode(str(item.getId()))
            title_node.appendChild(title)
            entry.appendChild(title_node)
            summary_node = doc.createElement("summary")
            summary_node.setAttribute("type", "html")
            description = [item.description.encode('utf-8').decode('utf-8')]
            description.append("<b>Address</b>: %s" % item.geo_location.address.encode('utf-8').decode('utf-8'))
            if hasattr(item.aq_self, 'webpage'):
                description.append("<b>Webpage:</b>: %s" % item.webpage.encode('utf-8').decode('utf-8'))
            if hasattr(item.aq_self, 'contact'):
                description.append("<b>Contact:</b>: %s" % item.contact.encode('utf-8').decode('utf-8'))
            if hasattr(item.aq_self, 'source') and item.source:
                description.append("<b>Source:</b>: %s" % item.source.encode('utf-8').decode('utf-8'))
            summary_node.appendChild(doc.createTextNode("%s" % ("<br />".join(description))))
            entry.appendChild(summary_node)

            type_node = doc.createElement("georss:featuretypetag")
            coords = doc.createTextNode(self.getSymbol(item.geo_type).title)
            type_node.appendChild(coords)
            entry.appendChild(type_node)

            geo_node = doc.createElement("georss:point")
            coords = doc.createTextNode("%s %s" % (item.geo_location.lat, item.geo_location.lon))
            geo_node.appendChild(coords)
            entry.appendChild(geo_node)

            try:
                rss.append(entry.toprettyxml())
            except UnicodeDecodeError:
                print entry
        if REQUEST:
            REQUEST.RESPONSE.setHeader('Content-Type', 'application/atom+xml')
            REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=locations.xml')
        rss.append("</feed>")
        return '\n'.join(rss)

    security.declareProtected(view, 'get_geotaggable_meta_types')
    def get_geotaggable_meta_types(self):
        """Returns a list of geotaggable meta types"""
        installed_content_metatypes = self.get_pluggable_installed_meta_types()
        schemas = self.portal_schemas
        res = []
        for meta_type in installed_content_metatypes:
            schema = schemas.getSchemaForMetatype(meta_type)
            if schema:
                try:
                    geo_location = schema.getWidget('geo_location');
                    geo_type = schema.getWidget('geo_type');
                except KeyError:
                    # one or both widgets are missing; skip it
                    continue
                if geo_location.visible and geo_type.visible:
                    res.append(meta_type)
        return res

    #alias for yahoo api key getter
    #used for render_object_map
    get_yahooApiKey = get_mapsapikey
    def render_object_map(self, geo_location, default=None):
        """
        Returns all the script and html required to display a map
        corresponding to the map engine selected in the administration
        area. The constrains of the map are affected by self.detailed_* 
        attributes.
        
        geo_location -- a Geo() object
        
        Example usage:
        <tal:block content="structure python:here.portal_map.render_object_map(here.geo_location)"/>
        """
        if not geo_location:
            if default:
                geo_location = default
            else:
                return ''

        map_types = {'REG': {'google': 'G_NORMAL_MAP', 'yahoo': 'YAHOO_MAP_REG'},
                     'HYB': {'google': 'G_HYBRID_MAP', 'yahoo': 'YAHOO_MAP_HYB'},
                     'SAT': {'google': 'G_SATELLITE_MAP', 'yahoo': 'YAHOO_MAP_SAT'},
                     }
        
        if geo_location.missing_lat_lon:
            lat, lon = "''", "''"
        else:
            lat, lon = geo_location.lat, geo_location.lon
        address = json.dumps(geo_location.address)
        if address == '""':
            address = json.dumps(self.center_locality.strip())
        all_map_types = [map_types[x[-3:]][self.map_engine] for x in self.map_types]
        default_map_type = map_types[self.default_type[-3:]][self.map_engine]
        dom_element = "map"
        template_id = "%s_map.html" % self.map_engine
        template = get_template(template_id, skip_script=True)
        appid = getattr(self, "get_%sApiKey" % self.map_engine)()
        template = template % (appid, lat, lon, address, self.detailed_zoom,
                               all_map_types, default_map_type, dom_element)
        map_div = get_template('map_div.html', skip_script=True)
        map_div = map_div % (self.detailed_map_width, self.detailed_map_width, 
                             self.detailed_map_height, self.absolute_url())
        return '\n'.join((map_div, template))

    def render_edit_map(self, geo_location):
        return self.render_object_map(geo_location, default=Geo(0,0))

    security.declareProtected(view, 'suggest_location_redirect')
    def suggest_location_redirect(self, REQUEST, content_type, folder, url=None):
        """ """
        if not folder and not url:
            raise ValueError, 'No value given for folder'

        # set url from folder or url
        start_url = '/%s' % folder
        if start_url == '/':
            start_url = url

        pc = self.get_pluggable_content()
        for item in pc.values():
            if item['schema_name'] == content_type:
                return REQUEST.RESPONSE.redirect('%s/%s' %
                    (start_url, item['add_form']))
        raise ValueError, 'Could not add this content type to the folder'

    security.declareProtected(view, 'suggest_location')
    suggest_location = PageTemplateFile('zpt/suggest_location', globals())

    admin_tabs = [
        {'url': 'admin_map_html', 'title': 'General settings'},
        {'url': 'admin_map_contenttypes_html', 'title': 'Content types'},
        {'url': 'admin_maptypes_html', 'title': 'Location categories'},
        {'url': 'admin_maplocations_html', 'title': 'Manage locations'},
        {'url': 'admin_mapduplicatelocations_html', 'title': 'Duplicate locations'},
        {'url': 'admin_map_no_coordinates_html', 'title': 'Objects with no coordinates'}
    ]
    admin_pt = PageTemplateFile('zpt/map_admin_template', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_map_html')
    admin_map_html = PageTemplateFile('zpt/map_edit', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_map_contenttypes_html')
    admin_map_contenttypes_html = PageTemplateFile('zpt/map_contenttypes', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_maptypes_html')
    admin_maptypes_html = PageTemplateFile('zpt/map_symbols', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_maplocations_html')
    admin_maplocations_html = PageTemplateFile('zpt/map_locations', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_mapduplicatelocations_html')
    admin_mapduplicatelocations_html = PageTemplateFile('zpt/map_duplicate_locations', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_map_no_coordinates_html')
    admin_map_no_coordinates_html = PageTemplateFile('zpt/map_no_coordinates', globals())

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
