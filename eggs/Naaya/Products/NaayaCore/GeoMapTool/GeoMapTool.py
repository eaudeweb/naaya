"""This tool is used to manage map engines (google, yahoo, bing, etc.)
in a Naaya Site. This tool is related to naaya.content.geopoint and SchemaTool's
GeoWidget that can be used to display points on a map for different content
types. Other features include map clustering, kml exports, and searching.

"""

from decimal import Decimal
from datetime import datetime
import time
from xml.dom import minidom
import simplejson as json
import operator
from warnings import warn

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from App.ImageFile import ImageFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

from zope.interface import implements
from interfaces import IGeoMapTool

from Products.NaayaBase.constants import *
import Products.NaayaBase.NyContentType
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaCore.managers.session_manager import session_manager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.SchemaTool.widgets.geo import Geo, geo_as_json
from Products.NaayaCore.SchemaTool.widgets.geo import json_encode_helper
from Products.NaayaCore.GeoMapTool import clusters_catalog
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core.zope2util import path_in_site, get_template_source
from naaya.core import ggeocoding

from managers.symbols_tool import symbols_tool
from managers.kml_gen import kml_generator

all_engines = {}

def register_map_engine(cls):
    all_engines[cls.name] = cls

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

def err_info():
    import sys, traceback
    return traceback.format_exception_only(*sys.exc_info()[:2])[-1].strip()

class GeoMapTool(Folder, utils, session_manager, symbols_tool):
    """
    Class that implements the tool.
    """

    implements(IGeoMapTool)

    #center map in Europe
    _cluster_pngs = [ImageFile('images/cluster_about_10.png', globals()),
                        ImageFile('images/cluster_about_20.png', globals()),
                        ImageFile('images/cluster_about_50.png', globals()),
                        ImageFile('images/cluster_about_100.png', globals()),
                        ImageFile('images/cluster_about_200.png', globals()),
                        ImageFile('images/cluster_about_500.png', globals()),
                        ImageFile('images/cluster_about_1000.png', globals()),
                        ImageFile('images/cluster_2000_more.png', globals())]

    def _pick_cluster(self, len_group):
        if len_group < 15:
            return 0 # about 10
        elif len_group < 30:
            return 1 # about 20
        elif len_group < 75:
            return 2 # about 50
        elif len_group < 150:
            return 3 # about 100
        elif len_group < 300:
            return 4 # about 200
        elif len_group <= 750:
            return 5 # about 500
        elif len_group <= 2000:
            return 6 # about 1000
        else:
            return 7

    _marker_template = NaayaPageTemplateFile('zpt/map_marker_popup', globals(),
                                          'map_marker_popup')
    _small_marker_template = NaayaPageTemplateFile('zpt/map_small_marker_popup', globals(),
                                          'map_small_marker_popup')

    def get_small_marker(self, object):
        has_access = bool(self.REQUEST.AUTHENTICATED_USER.has_permission(permission=view,
                                                                        object=object))
        access_str = ''
        if not has_access:
            access_str = '(RESTRICTED ACCESS)'
        return self._small_marker_template(object=object, access_str=access_str)

    def get_marker(self, object):
        has_access = bool(self.REQUEST.AUTHENTICATED_USER.has_permission(permission=view,
                                                                        object=object))
        access_str = ''
        if not has_access:
            access_str = '<div>RESTRICTED ACCESS</div>'
        translate = self.getSite().getPortalTranslations()
        return self._marker_template(object=object, access_str=access_str)


    meta_type = METATYPE_GEOMAPTOOL
    icon = 'misc_/NaayaCore/GeoMapTool.gif'

    security = ClassSecurityInfo()

    manage_options = Folder.manage_options[:2] + (
        {'label': 'Admin', 'action': 'admin_map_html'},
    ) + Folder.manage_options[2:]

    cluster_points = True
    initial_zoom = None

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        symbols_tool.__dict__['__init__'](self)
        self.initial_address = u'Europe'
        self.map_height_px = 500
        self.objmap_height_px = 400
        self.objmap_width_px = 400
        self.objmap_zoom = 14
        self.set_map_engine('google')

    def _create_map_engine_if_needed(self):
        name = self.current_engine
        obj_id = 'engine_%s' % name
        if obj_id not in self.objectIds():
            self._setObject(obj_id, all_engines[name](id=obj_id))

    security.declarePrivate('set_map_engine')
    def set_map_engine(self, name):
        self.current_engine = name
        self._create_map_engine_if_needed()

    security.declarePrivate('get_map_engine')
    def get_map_engine(self, engine_name=None):
        if engine_name is None:
            engine_name = self.current_engine
        return self['engine_%s' % engine_name]

    def can_filter_by_first_letter(self):
        catalog_tool = self.getCatalogTool()
        return catalog_tool._catalog.indexes.has_key('full_title')

    security.declarePrivate('build_geo_filters')
    def build_geo_filters(self, path='', meta_types=None, geo_types=[],
            approved=True,
            landscape_type=[], administrative_level=[], topics=[],
            lat_min=-90., lat_max=90., lon_min=-180., lon_max=180.,
            query='', country='', first_letter=None,
            **kwargs):
        base_filter = {}

        base_filter['path'] = path

        if meta_types is None:
            base_filter['meta_type'] = self.get_geotaggable_meta_types()
        else:
            base_filter['meta_type'] = meta_types

        if geo_types:
            base_filter['geo_type'] = geo_types

        if approved:
            base_filter['approved'] = 1

        if landscape_type:
            base_filter['landscape_type'] = landscape_type

        if topics:
            base_filter['topics'] = topics

        if administrative_level:
            base_filter['administrative_level'] = administrative_level

        if country:
            base_filter['coverage'] = country

        base_filter['geo_latitude'] = {'query': (Decimal(str(lat_min)), Decimal(str(lat_max))),
                                        'range':'min:max'}
        base_filter['geo_longitude'] = {'query': (Decimal(str(lon_min)), Decimal(str(lon_max))),
                                        'range':'min:max'}

        filters = []
        filters.append(base_filter)

        custom_filter = self._getOb('custom_filter', None)
        if custom_filter is not None:
            custom_filter(filters, kwargs)

        if query:
            query_filters = []
            for f in filters:
                for lang in self.gl_get_languages():
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
    def get_geo_objects(self, lat, lon, path='', geo_types=None, query=''):
        """ """

        eps = Decimal('0.000001')
        lat, lon = Decimal(lat), Decimal(lon)
        kwargs = {
            'lat_min': lat - eps,
            'lat_max': lat + eps,
            'lon_min': lon - eps,
            'lon_max': lon + eps,
            'path': path,
            'geo_types': geo_types,
            'query': query,
        }

        criteria = self._parse_search_terms(None, kwargs)
        filters = self.build_geo_filters(**criteria)
        results = self._search_geo_objects(filters)
        return results

    security.declarePrivate('_search_geo_objects')
    def _search_geo_objects(self, filters):
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

        return map(lambda rid: catalog_tool.getobject(rid), rids)

    def _sort_geo_objects(self, objects, sort_on, sort_order):
        key_func = None
        if sort_on == 'title':
            key_func = lambda x: x.title
        elif sort_on == 'geo_address':
            key_func = lambda x: x.geo_location.address
        elif sort_on == 'geo_latitude':
            key_func = lambda x: x.geo_location.lat
        elif sort_on == 'geo_longitude':
            key_func = lambda x: x.geo_location.lon
        elif sort_on == 'coverage':
            key_func = lambda x: x.coverage

        reverse = (sort_order == 'reverse')

        if key_func is not None:
            objects.sort(key=key_func, reverse=reverse)

    security.declareProtected(view, 'search_geo_objects')
    def search_geo_objects(self, sort_on='', sort_order='',
                           REQUEST=None, **kwargs):
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

        criteria = self._parse_search_terms(REQUEST, kwargs)

        if criteria['lon_min'] < criteria['lon_max']:
            filters = self.build_geo_filters(**criteria)
            results = self._search_geo_objects(filters)

        else:
            filters1 = self.build_geo_filters(**dict(criteria, lon_max=180.0))
            results1 = self._search_geo_objects(filters1)

            filters2 = self.build_geo_filters(**dict(criteria, lon_min=-180.0))
            results2 = self._search_geo_objects(filters2)

            results = results1 + results2

        self._sort_geo_objects(results, sort_on, sort_order)
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
                            group_paths = [clusters_catalog.getObjectPathFromCatalog(catalog_tool, rid)
                                           for rid in groups[i]]
                            cluster_obs.append((centers[i], group_paths))

        return cluster_obs, single_obs

    def _parse_search_terms(self, REQUEST, kwargs):
        criteria = {
            'lat_min': None,
            'lat_max': None,
            'lon_min': None,
            'lon_max': None,
            'path': '',
            'query': '',
            'approved': True,
            'topics': [],
            'landscape_type': [],
            'administrative_level': [],
            'country': '',
            'languages': None,
            'meta_types': None,
        }
        if REQUEST is not None:
            criteria.update(REQUEST.form)
        criteria.update(kwargs)

        coord_defaults = {
            'lat_min': -90.0,
            'lat_max': 90.0,
            'lon_min': -180.0,
            'lon_max': 180.0,
        }
        for name, default_value in coord_defaults.iteritems():
            if criteria[name] in (None, ''):
                criteria[name] = default_value
            else:
                criteria[name] = float(criteria[name])

        if 'geo_query' in criteria:
            criteria['query'] = criteria['geo_query']
            del criteria['geo_query']

        if 'geo_types' in criteria:
            if isinstance(criteria['geo_types'], str):
                if criteria['geo_types'] == '':
                    criteria['geo_types'] = []
                else:
                    criteria['geo_types'] = criteria['geo_types'].split(',')
        else:
            criteria['geo_types'] = []

        for ignored_key in ['center', 'zoom', 'address']:
            if ignored_key in criteria:
                del criteria[ignored_key]

        return criteria

    security.declareProtected(view, 'search_geo_clusters')
    def search_geo_clusters(self, REQUEST=None, **kwargs):
        """ Returns all the clusters that match the specified criteria. """

        criteria = self._parse_search_terms(REQUEST, kwargs)

        if criteria['lon_min'] < criteria['lon_max']:
            filters = self.build_geo_filters(**criteria)
            cluster_obs, single_obs = self._search_geo_clusters(filters)

        else:
            filters1 = self.build_geo_filters(**dict(criteria, lon_max=180.0))
            cluster_obs_1, single_obs_1 = self._search_geo_clusters(filters1)

            filters2 = self.build_geo_filters(**dict(criteria, lon_min=-180.0))
            cluster_obs_2, single_obs_2 = self._search_geo_clusters(filters2)

            cluster_obs = cluster_obs_1 + cluster_obs_2
            single_obs = single_obs_1 + single_obs_2

        return cluster_obs, single_obs

    map_kml = NaayaPageTemplateFile('zpt/map_kml', globals(),
                                          'Products.NaayaCore.GeomapTool.map_kml')
    
    security.declareProtected(view, 'downloadLocationsKml')
    def downloadLocationsKml(self, REQUEST):
        """Returns the selected locations as a KML file"""

        points = []
        for loc in self.search_geo_objects(REQUEST=REQUEST):
            if loc.geo_location is not None:
                points.append(loc)
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/vnd.google-earth.kml+xml')
        REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=locations.kml')
        return self.map_kml(points=points)

    security.declareProtected(view, 'xrjs_getGeoPoints')
    def xrjs_getGeoPoints(self, REQUEST):
        """ """
        try:
            points = []
            for res in self.search_geo_objects(REQUEST=REQUEST):
                if res.geo_location is None:
                    continue
                points.append({
                    'lat': res.geo_location.lat,
                    'lon': res.geo_location.lon,
                    'id': path_in_site(res),
                    'label': res.title_or_id(),
                    'icon_name': 'mk_%s' % res.geo_type,
                    'tooltip': self.get_marker(res),
                })

            json_response = json.dumps({'points': points},
                                       default=json_encode_helper)

        except:
            self.log_current_error()
            json_response = json.dumps({'error': err_info(), 'points': {}})

        REQUEST.RESPONSE.setHeader('Content-type', 'application/json')
        return json_response

    security.declareProtected(view, 'xrjs_getGeoClusters')
    def xrjs_getGeoClusters(self, REQUEST):
        """ """
        try:
            points = []
            cluster_obs, single_obs = self.search_geo_clusters(REQUEST)

            for center, grouped_ids in cluster_obs:
                points.append({
                    'lat': center.lat,
                    'lon': center.lon,
                    'id': '',
                    'label': 'cluster',
                    'icon_name': ('mk_cluster_%s' %
                                  self._pick_cluster(len(grouped_ids))),
                    'tooltip': '',
                    'num_records': len(grouped_ids),
                    'point_ids': grouped_ids,
                })

            for res in single_obs:
                if res.geo_location is None:
                    continue
                if not res.geo_type:
                    #TODO: add logging?
                    continue
                points.append({
                    'lat': res.geo_location.lat,
                    'lon': res.geo_location.lon,
                    'id': path_in_site(res),
                    'label': res.title_or_id(),
                    'icon_name': 'mk_%s' % res.geo_type,
                    'tooltip': self.get_marker(res),
                })

            response_data = {'points': points}

        except:
            self.log_current_error()
            response_data = {'error': err_info(), 'points': {}}

        json_response = json.dumps(response_data, default=json_encode_helper)

        REQUEST.RESPONSE.setHeader('Content-type', 'application/json')
        return json_response


    security.declareProtected(view, 'xrjs_getPointBalloon')
    def xrjs_getPointBalloon(self, point_id):
        """ get the map balloon for point  """
        # we do unrestricted traverse because `get_marker` will check perms

        site = self.getSite()
        if isinstance(point_id, list):
            # multiple points requested
            out = ''
            for pth in point_id:
                ob = site.unrestrictedTraverse(pth, None)
                if ob is not None:
                    out += self.get_small_marker(ob)
            return out
        else:
            ob = site.unrestrictedTraverse(point_id)
            return self.get_marker(ob)

    security.declareProtected(view, 'xrjs_getTooltip')
    def xrjs_getTooltip(self, lat, lon, path='', geo_types=None, geo_query=None):
        """ """
        warn("`xrjs_getTooltip` is deprecated. Use `xrjs_getPointBalloon` "
             "instead.")
        obs = self.get_geo_objects(lat, lon, path, geo_types, geo_query)
        if len(obs) == 1:
            return self.utToUtf8(self.get_marker(obs[0]))

        ret = ''
        for ob in obs:
            ret += self.get_small_marker(ob)
        return ret

    def get_geotype_icons(self):
        for i in range(len(self._cluster_pngs)):
            yield {
                'id': "cluster_%d" % i,
                'url': ('%s/getSymbolPicture?id=symbol_cluster_%d' %
                        (self.absolute_url(), i)),
                'w': 32,
                'h': 32,
                'color': None,
            }

        for symbol in self.getSymbolsList():
            size = symbol.image_size
            yield {
                'id': symbol.id,
                'url': ('%s/getSymbolPicture?id=%s' %
                        (self.absolute_url(), symbol.id)),
                'w': size.w,
                'h': size.h,
                'color': symbol.color,
            }

    def get_location_marker(self, location):
        symbol = self.getSymbol(location.geo_type)
        if symbol:
            icon_url = '%s/getSymbolPicture?id=%s' % (self.absolute_url(), symbol.id)
            if icon_url is not None:
                return icon_url
            return ''
        return ''

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getDuplicateLocations')
    def getDuplicateLocations(self, criteria, sort_on="", sort_order=""):
        """Returns a list of duplicate locations.

            It accepts the same parameters as :meth:`getLocations`.
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminAddSymbol')
    def adminAddSymbol(self, title='', description='', parent='',
                       color='', picture='', sortorder='', REQUEST=None):
        """ """
        if color:
            picture = None
        else:
            color = None

        try:
            id = 'symbol%s' % self.utGenRandomId(3)
            self.addSymbol(id, title, description, parent,
                           color, picture, sortorder)
        except ValueError, e:
            if REQUEST is None:
                raise
            self.setSessionErrorsTrans(e)
            return REQUEST.RESPONSE.redirect('%s/admin_maptypes_html'
                                              % self.absolute_url())

        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html'
                                       % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminUpdateSymbol')
    def adminUpdateSymbol(self, id='', title='', description='', parent='',
                          color='', picture='', sortorder='', REQUEST=None):
        """ """
        if color:
            picture = None
        else:
            color = None

        try:
            self.updateSymbol(id, title, description, parent,
                              color, picture, sortorder)
        except ValueError, e:
            if REQUEST is None:
                raise
            self.setSessionErrorsTrans(e)
            return REQUEST.RESPONSE.redirect('%s/admin_maptypes_html?id=%s'
                                              % (self.absolute_url(), id))

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html'
                                       % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'adminDeleteSymbols')
    def adminDeleteSymbols(self, id=[], REQUEST=None):
        """ """
        self.deleteSymbol(self.utConvertToList(id))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_maptypes_html' % self.absolute_url())

    security.declareProtected(view, 'getSymbolsListOrdered')
    def getSymbolsListOrdered(self, skey='sortorder', rkey=0):
        """ return an ordered lsit of symbols """
        r = []
        for p in self.getParentsListOrdered():
            r.append(p)
            r.extend(self.getSymbolChildrenOrdered(p.id))
        return r

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_set_contenttypes')
    def admin_set_contenttypes(self, geotag=[], REQUEST=None):
        """ """
        schema_tool = self.getSite().getSchemaTool()
        return schema_tool.admin_set_contenttypes(geotag=geotag, REQUEST=REQUEST)

    def list_geotaggable_types(self):
        schema_tool = self.getSite().getSchemaTool()
        return schema_tool.list_geotaggable_types()

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None):
        """ """
        return self._index_template()({'here': self})

    security.declareProtected(view_management_screens,
                              'manage_customize_index')
    def manage_customize_index(self, REQUEST):
        """ create a custom map_index """
        if 'map_index' in self.objectIds():
            raise ValueError('map_index already customized')
        else:
            text = get_template_source(self._index_template())
            manage_addPageTemplate(self, id='map_index', title='', text=text)
            REQUEST.RESPONSE.redirect('%s/manage_workspace' %
                                      self.map_index.absolute_url())

    def _index_template(self):
        if 'map_index' in self.objectIds():
            return self._getOb('map_index')
        else:
            return self.view_map_html

    security.declareProtected(view, 'view_map_html')
    view_map_html = NaayaPageTemplateFile('zpt/map_index', globals(),
                                          'map_index')

    security.declareProtected(view, 'embed_map_html')
    _embed_map_html = NaayaPageTemplateFile('zpt/map_embed', globals(),
                                            'map_embed')
    def embed_map_html(self, REQUEST):
        """ embeddable map, for iframe """
        if 'map_embed' in self.objectIds():
            return self.map_embed(REQUEST)
        else:
            return self._embed_map_html(REQUEST)

    _list_locations = NaayaPageTemplateFile('zpt/list_locations', globals(),
                                            'map_list_locations')
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
        geo_types = kw.get('geo_types', [])
        if geo_types == '':
            geo_types = []
        if isinstance(geo_types, str):
            geo_types = geo_types.split(',')
        administrative_level = kw.get('administrative_level', [])
        if administrative_level == '':
            administrative_level = []
        if isinstance(administrative_level, str):
            administrative_level = administrative_level.split(',')
        landscape_type = kw.get('landscape_type', [])
        if landscape_type == '':
            landscape_type = []
        if isinstance(landscape_type, str):
            landscape_type = landscape_type.split(',')
        topics = kw.get('topics', [])
        if topics == '':
            topics = []
        if isinstance(topics, str):
            topics = topics.split(',')
        geo_query = kw.get('geo_query', '')
        country = kw.get('country', '')

        sort_on, sort_order = '', ''
        if kw.get('sortable', ''):
            sort_on = kw.get('sort_on', '')
            sort_order = kw.get('sort_order', '')

        first_letter = kw.get('first_letter', '')

        results = self.search_geo_objects(
            lat_min=lat_min, lat_max=lat_max, lon_min=lon_min,
            lon_max=lon_max, geo_types=geo_types, query=geo_query,
            administrative_level=administrative_level,
            landscape_type=landscape_type, topics=topics,
            first_letter=first_letter, sort_on=sort_on, sort_order=sort_order,
            country=country,
        )
        options = {}
        options['lat_min'] = lat_min
        options['lat_max'] = lat_max
        options['lon_min'] = lon_min
        options['lon_max'] = lon_max
        options['geo_types'] = geo_types
        options['administrative_level'] = administrative_level
        options['landscape_type'] = landscape_type
        options['topics'] = topics
        options['geo_query'] = geo_query
        options['country'] = country
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
        options['ratable_records'] = self._ratable_results(results[options['start']:options['end']])
        return self._list_locations(**options)

    def _ratable_results(self, results):
        for ob in results:
            try:
                ratable = ob.is_ratable()
                if ratable: return True
            except: pass
        return False

    security.declareProtected(view, 'export_csv')
    def export_csv(self, meta_type, REQUEST=None, RESPONSE=None, **kw):
        """
        Should be used to export the map viewable objects of a given meta_type
        The exported properties are taken from schema (similar to the global csv_export)
        """
        schema = self.getSite().getSchemaTool().getSchemaForMetatype(meta_type)
        if schema is None:
            raise ValueError('Schema for meta-type "%s" not found' % meta_type)

        if REQUEST is not None:
            kw.update(REQUEST.form)

        if 'meta_type' in kw:
            del kw['meta_type']

        objects = self.search_geo_objects(meta_types=[meta_type], **kw)

        csv_export = self.getSite().csv_export
        ret = csv_export.generate_csv_output(meta_type, objects)

        RESPONSE.setHeader('Content-Type', 'text/x-csv')
        RESPONSE.setHeader('Content-Length', len(ret))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="map_contacts.csv"')

        return ret

    security.declareProtected(view, 'export_geo_rss')
    def export_geo_rss(self, sort_on='', sort_order='',
                       REQUEST=None, **kwargs):
        """ """
        timestamp = datetime.fromtimestamp(time.time())
        timestamp = str(timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        rss = ["""<feed xmlns="http://www.w3.org/2005/Atom" xmlns:georss="http://www.georss.org/georss">
              <title>%s</title>
              <id>%s</id>
              <link rel="self" href="%s" />
              <author><name>European Environment Agency</name></author>
              <updated>%s</updated>
              """ % (self.title, self.absolute_url(), self.absolute_url(), timestamp) ]
        items = self.search_geo_objects(REQUEST=REQUEST, sort_on=sort_on,
                                        sort_order=sort_order, **kwargs)

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

    _object_index_map = PageTemplateFile('zpt/object_index_map', globals())
    def render_object_map(self, geo_location):
        """
        Returns all the script and html required to display a map
        corresponding to the map engine selected in the administration
        area.

        `geo_location` -- a ``Geo`` object

        Example usage::
                <tal:block condition="python:here.prop_details('geo_location')['show']"
                    content="structure python:here.portal_map.render_object_map(here.geo_location)"/>
        """

        if not geo_location or geo_location.missing_lat_lon:
            return ''

        return self._object_index_map(coord_json=geo_as_json(geo_location))

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
        {'url': 'admin_maptypes_html', 'title': 'Location categories'},
        {'url': 'admin_maplocations_html', 'title': 'Manage locations'},
        {'url': 'admin_mapduplicatelocations_html', 'title': 'Duplicate locations'},
        {'url': 'admin_map_no_coordinates_html', 'title': 'Objects with no coordinates'}
    ]
    admin_pt = PageTemplateFile('zpt/map_admin_template', globals())

    admin_map_embed_help = NaayaPageTemplateFile('zpt/map_embed_help',
                    globals(), 'site_admin_map_embed_help')

    _admin_map_html = PageTemplateFile('zpt/map_edit', globals())
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_map_html')
    def admin_map_html(self, REQUEST):
        """ configure the map """
        self._create_map_engine_if_needed()
        options = {
            'all_engines': sorted([
                {'name': name, 'label': engine.title}
                for name, engine in all_engines.iteritems()],
                    key=operator.itemgetter('name')),
            'engine_config_html': self.get_map_engine().config_html(),
        }
        return self._admin_map_html(REQUEST, **options)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'manageProperties')
    def manageProperties(self, REQUEST):
        """ """
        form = dict(REQUEST.form)
        form.setdefault('cluster_points', False)
        for key in ('initial_address', 'map_height_px',
                    'objmap_height_px', 'objmap_width_px', 'objmap_zoom',
                    'cluster_points'):
            setattr(self, key, form[key])
        if form['initial_zoom']:
            self.initial_zoom = int(form['initial_zoom'])
        else:
            self.initial_zoom = None

        new_engine = form['engine']
        if new_engine != self.current_engine:
            self.set_map_engine(new_engine)
        else:
            self.get_map_engine().save_config(form)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/admin_map_html' %
                                      self.absolute_url())

    security.declarePublic('setup_map_engine_html')
    def setup_map_engine_html(self, request, **kwargs):
        """ render the HTML needed to set up the current map engine """
        kwargs.update(request.form)

        global_config = {
            'initial_address': self.initial_address,
            'initial_zoom': self.initial_zoom,
            'icons': list(self.get_geotype_icons()),
            'objmap_zoom': self.get_object_map_zoom_level(),
            'cluster_points': self.cluster_points,
        }
        global_config.update(kwargs)

        engine = self.get_map_engine(kwargs.get('map_engine', None))
        return engine.html_setup(request, global_config)

    def get_object_map_zoom_level(self):
        if self.current_engine == 'yahoo':
            return 18 - self.objmap_zoom
        elif self.current_engine in ['google', 'bing', 'openlayers']:
            return self.objmap_zoom
        else:
            return None

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

    # macros
    security.declareProtected(view, 'locations_table_html')
    locations_table_html = PageTemplateFile('zpt/locations_table', globals())

    security.declareProtected(view, 'map_i18n_js')
    def map_i18n_js(self, REQUEST):
        """ translations for javascript map messages """
        #TODO: deprecated; replace with `i18n_js` from NySite.
        lang = self.gl_get_selected_language()
        translations_js = self.getSite().i18n_js(lang=lang)
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/javascript')
        return translations_js + 'var naaya_map_i18n = naaya_i18n_catalog;'

    security.declareProtected(view_management_screens, 'manage_test_html')
    manage_test_html = PageTemplateFile('zpt/manage_test', globals())

    security.declareProtected(view, 'get_default_style')
    def get_default_style(self):
        """ Return the style from the beginning of the file as string
        so we can get ZMI to let us customize the kml template """
        kml = kml_generator()
        return kml.get_default_style()

    security.declareProtected(view, 'open_style')
    def open_style(self, id):
        """ Return the <style> tag as string
        so we can get ZMI to let us customize the kml template """
        kml = kml_generator()
        return kml.open_style(id)

    security.declareProtected(view, 'close_style')
    def close_style(self):
        """ Return the </style> tag as string
        so we can get ZMI to let us customize the kml template """
        kml = kml_generator()
        return kml.close_style()

    def _google_geocode(self, address):
        try:
            result = ggeocoding.geocode2(address)
        except ggeocoding.GeocoderServiceError, e:
            return {'error': e.message}
        else:
            # allow for returning multiple results
            return [result]

    def geocode(self, REQUEST):
        """ geocode using the google service """
        result = self._google_geocode(REQUEST.form['address'])
        REQUEST.RESPONSE.setHeader('Content-type', 'application/json')
        return json.dumps(result)

InitializeClass(GeoMapTool)
