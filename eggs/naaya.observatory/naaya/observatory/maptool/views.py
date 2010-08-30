import simplejson as json
from random import randint, choice
from time import time
from datetime import datetime, timedelta

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import manage_addFieldIndex
from BTrees.IIBTree import IISet, union, weightedIntersection
from App.Common import rfc1123_date
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.NaayaCore.GeoMapTool.clusters_catalog import _apply_index_with_range_dict_results, getObjectFromCatalog
from Products.NaayaCore.GeoMapTool import clusters

from session import SessionManager
from utils import RATING_VALUES, TYPE_VALUES
from utils import query_reverse_geocode, map_icon, map_distance
from clusters_catalog import filter_rids

RESOURCES_PATH = '++resource++naaya.observatory.maptool'
IMAGES_PATH = RESOURCES_PATH + '/images'

RATING_IMAGE_NAMES = ['very-bad', 'bad', 'average', 'good', 'very-good']
RATING_IMAGE_PATHS = ['%s/%s.png' % (IMAGES_PATH, f)
                        for f in RATING_IMAGE_NAMES]

TYPE_IMAGE_NAMES = ['vegetation', 'water', 'soil', 'citizens']
TYPE_IMAGE_PATHS = ['%s/%s.png' % (IMAGES_PATH, f)
                    for f in TYPE_IMAGE_NAMES]

class MapView(SessionManager):
    """A view for the observatory map"""

    def __init__(self, context, request):
        self.context = context
        self.site = context.getSite()
        self.request = request
        self.portal_map = context.getGeoMapTool()

    def map_icon(self, rating, type, RESPONSE, number=None):
        ret = map_icon(rating, type, number)

        RESPONSE.setHeader('Content-Type', 'image/png')
        RESPONSE.setHeader('Cache-Control', 'public,max-age=86400')
        RESPONSE.setHeader('Expires', rfc1123_date(time() + 86400))

        return ret

    def xrjs_getClusters(self, lat_min, lat_max, lon_min, lon_max):
        """ """
        tc_start = time()
        lat_min, lat_max = float(lat_min), float(lat_max)
        lon_min, lon_max = float(lon_min), float(lon_max)

        grid_size = 7
        tlat_min, tlat_max, tlon_min, tlon_max = clusters.get_discretized_limits(
            lat_min, lat_max, lon_min, lon_max, grid_size)

        catalog = self.context.catalog
        rating_idx = catalog._catalog.indexes['rating']

        lat_idx = catalog._catalog.indexes['latitude']
        lon_idx = catalog._catalog.indexes['longitude']
        lat_set, lat_dict = _apply_index_with_range_dict_results(lat_idx._index, tlat_min, tlat_max)
        lon_set, lon_dict = _apply_index_with_range_dict_results(lon_idx._index, tlon_min, tlon_max)

        type_idx = catalog._catalog.indexes['type']
        tyle_set, type_dict = _apply_index_with_range_dict_results(type_idx._index)

        tc_start_id_idx = time()
        id_idx = catalog._catalog.indexes['id']
        id_set, id_dict = _apply_index_with_range_dict_results(id_idx._index)
        tc_end_id_idx = time()
        print 'id_idx', tc_end_id_idx - tc_start_id_idx


        map_filters = {'latitude': {'query': (tlat_min, tlat_max),
                                    'range': 'min:max'},
                       'longitude': {'query': (tlon_min, tlon_max),
                                     'range': 'min:max'}}
        rids = filter_rids(catalog, map_filters)
        if rids is None:
            r_list = []
        else:
            r_list = list(set(rids))

        def make_points_by_type():

            # transform objects to points
            points_by_type = {}
            for i, rid in enumerate(r_list):
                point = clusters.Point(i, float(lat_dict[rid]), float(lon_dict[rid]))
                type = type_dict[rid]
                if not points_by_type.has_key(type):
                    points_by_type[type] = []
                points_by_type[type].append(point)
            return points_by_type
        points_by_type = make_points_by_type()

        def make_centers():
            all_centers = []
            for type in TYPE_VALUES:
                if type not in points_by_type:
                    continue
                points = points_by_type[type]

                centers, groups = clusters.kmeans(tlat_min, tlat_max, tlon_min, tlon_max, points, grid_size)

                # get ratings for centers
                rating_set, rating_dict = _apply_index_with_range_dict_results(rating_idx._index)
                for i, g in enumerate(groups):
                    l_rat = []
                    for p in g:
                        p_rat = rating_dict[r_list[p.id]]
                        if p_rat is not None:
                            l_rat.append(rating_dict[r_list[p.id]])
                    if len(l_rat) > 0:
                        centers[i].averageRating = sum(l_rat) / float(len(l_rat))
                    else:
                        centers[i].averageRating = None
                    centers[i].group = g
                    centers[i].type = type
                all_centers.extend(centers)
            return all_centers
        centers = make_centers()

        def cluster_tooltip(ob):
            ids = [id_dict[r_list[p.id]] for p in ob.group]
            return self.cluster_index(ids)

        def build_point(ob):
            if len(ob.group) == 1:
                rid = r_list[ob.group[0].id]
                ob = getObjectFromCatalog(catalog, rid)
                icon_name = 'mk_single_rating_%s_%d' % (ob.type, ob.rating)
                return {'lon': ob.longitude,
                        'lat': ob.latitude,
                        'tooltip': '',
                        'label': '',
                        'icon_name': icon_name,
                        'id': ob.id}
            else:
                rating = int(ob.averageRating)
                display_tooltip = (lat_max - lat_min) < 1.
                if display_tooltip:
                    tooltip = cluster_tooltip(ob)
                else:
                    tooltip = ''
                num_points = len(ob.group)
                icon_name = 'mk_rating_%s_%d_%d' % (ob.type, rating, num_points)
                return {'lon': ob.lon,
                        'lat': ob.lat,
                        'tooltip': tooltip,
                        'display_tooltip': display_tooltip,
                        'label': 'cluster',
                        'icon_name': icon_name,
                        'num_points': num_points,
                        'id': ''}

        points = [build_point(c) for c in centers if c.averageRating]
        tc_end = time()
        print 'clusters', tc_end - tc_start
        return json.dumps({'points': points})

    def get_geotype_icons(self):
        # cluster images
        for rating in RATING_VALUES:
            for type in TYPE_VALUES:
                for count in range(1000+1):
                    id = 'rating_%s_%d_%d' % (type, rating, count)
                    url = ('map_icon?type=%s&rating=%s&number=%s'
                                    % (type, rating, count))
                    yield {
                        'id': id,
                        'url': url,
                        'w': 38,
                        'h': 37,
                    }

        # single objects images
        for rating in RATING_VALUES:
            for type in TYPE_VALUES:
                id = 'single_rating_%s_%d' % (type, rating)
                url = ('map_icon?type=%s&rating=%s'
                                % (type, rating))
                yield {
                        'id': id,
                        'url': url,
                        'w': 38,
                        'h': 37,
                }

    def setup_map_engine_html(self, request, **kwargs):
        """ render the HTML needed to set up the bing map engine """
        global_config = {
            'initial_address': self.portal_map.initial_address,
            'icons': list(self.get_geotype_icons()),
        }
        global_config.update(kwargs)
        map_engine = self.portal_map.get_map_engine()
        return map_engine.html_setup(request, global_config)


    def submit_pin(self, lat, lon, address, country, type, rating,
            REQUEST, comment=None):
        """ """
        lat, lon = float(lat), float(lon)
        rating = int(rating)
        date = datetime.now()
        author, session_key = self.get_author_and_session(REQUEST)

        pin_id = self.context.add_pin(type, lat, lon, address, country,
                rating, comment, date, author, session_key)

    def add_random_pins(self, num, REQUEST):
        num = int(num)
        for i in range(num):
            lat = randint(-89*100, 89*100)/100.
            lon = randint(-179*100, 179*100)/100.
            type = choice(TYPE_VALUES)
            rating = choice(RATING_VALUES)

            year = randint(1900, 2010)
            month = randint(1, 12)
            day = randint(1, 28)
            date = datetime(year, month, day)

            # like submit_pin except date was already generated
            lat, lon = float(lat), float(lon)
            rating = int(rating)
            author, session_key = self.get_author_and_session(REQUEST)

            pin_id = self.context.add_pin(type, lat, lon, '', '',
                    rating, '', date, author, session_key)

    def get_pin_by_id(self, id):
        return self.context.get_pin(id)

    def short_string(self, s, limit):
        if len(s) <= limit:
            return s
        return s[:limit-3] + '...'

    def check_user_can_add_pin(self, lat, lon, author, session_key):
        """ """
        tc_start = time()
        catalog = self.context.catalog

        # modify if map_distance limit changes
        lat_min, lat_max = lat - 5., lat + 5.
        lon_min, lon_max = lon - 5., lon + 5.

        filters = {'latitude': {'query': (lat_min, lat_max),
                                'range': 'min:max'},
                   'longitude': {'query': (lon_min, lon_max),
                                 'range': 'min:max'},
                   'author': author,
                   'session_key': session_key}

        rids = filter_rids(catalog, filters)
        if rids is None:
            r_list = []
        else:
            r_list = list(set(rids))

        lat_idx = catalog._catalog.indexes['latitude']
        lon_idx = catalog._catalog.indexes['longitude']
        date_idx = catalog._catalog.indexes['date']

        _, lat_dict = _apply_index_with_range_dict_results(lat_idx._index, lat_min, lat_max)
        _, lon_dict = _apply_index_with_range_dict_results(lon_idx._index, lon_min, lon_max)
        _, date_dict = _apply_index_with_range_dict_results(date_idx._index)

        def convert_to_datetime(date_index_val):
            year = date_index_val / 535680
            month = (date_index_val / 44640) % 12
            day = (date_index_val / 1440) % 31
            hour = (date_index_val / 60) % 24
            minute = date_index_val % 60
            return datetime(year, month, day, hour, minute)

        ret = True
        for rid in r_list:
            clat, clon = lat_dict[rid], lon_dict[rid]
            if map_distance(lat, lon, clat, clon) < 1: #km
                cdate = convert_to_datetime(date_dict[rid])
                if datetime.now() - cdate < timedelta(weeks=1):
                    ret = False
                    break
        tc_end = time()
        print 'check user can add pin', tc_end - tc_start
        return ret

    _pin_add = ViewPageTemplateFile('zpt/pin_add.zpt', globals())
    def pin_add(self, latitude, longitude, REQUEST, type=None):
        """ """
        lat, lon = float(latitude), float(longitude)
        author, session_key = self.get_author_and_session(REQUEST)

        can_add = self.check_user_can_add_pin(lat, lon, author, session_key)

        if not can_add:
            return json.dumps({'can_add': can_add})

        address, country = query_reverse_geocode(lat, lon)
        html = self._pin_add(latitude=latitude,
                             longitude=longitude,
                             address=address,
                             country=country,
                             type=type)
        return json.dumps({'can_add': can_add, 'html': html})

    _cluster_index = ViewPageTemplateFile('zpt/cluster_index.zpt', globals())
    def cluster_index(self, point_ids, REQUEST=None):
        """ """
        points = [self.context.get_pin(id) for id in point_ids]
        return self._cluster_index(points=points)

