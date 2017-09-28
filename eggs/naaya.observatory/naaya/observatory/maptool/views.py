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

from Products.NaayaCore.GeoMapTool.clusters_catalog import (
        _apply_index_with_range_dict_results, getObjectFromCatalog)
from Products.NaayaCore.GeoMapTool.clusters import (
        get_discretized_limits, Point, kmeans)

from session import SessionManager
from observatory import RATING_VALUES, TYPE_VALUES
from utils import query_reverse_geocode, map_icon, map_distance, short_string
from clusters_catalog import filter_rids, get_index_dict


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
        def make_points(r_list, lan_dict, lon_dict, type_dict, rating_dict):
            points = []
            for i, rid in enumerate(r_list):
                point = Point(i, float(lat_dict[rid]), float(lon_dict[rid]))
                point.type = type_dict[rid]
                point.rating = rating_dict[rid]
                points.append(point)
            return points

        def make_points_by_type(points):
            points_by_type = {}
            for point in points:
                if not point.type in points_by_type:
                    points_by_type[point.type] = []

                points_by_type[point.type].append(point)
            return points_by_type

        def make_clusters(points_by_type, lat_min, lat_max,
                          lon_min, lon_max, grid_size):
            def average_rating(points):
                assert len(points) > 0

                ratings = [point.rating for point in points]
                return sum(ratings) / float(len(ratings))

            all_clusters = []
            for type, points in points_by_type.iteritems():
                centers, groups = kmeans(lat_min, lat_max,
                                                  lon_min, lon_max,
                                                  points, grid_size)
                clusters = []
                for i, points in enumerate(groups):
                    if len(points) > 0:
                        clusters.append({
                            'center': centers[i],
                            'points': points,
                            'type': type,
                            'averageRating': average_rating(points),
                            })

                all_clusters.extend(clusters)
            return all_clusters

        def point_data(cluster, r_list):
            def cluster_tooltip(cluster, r_list):
                cluster_rids = [r_list[point.id] for point in cluster['points']]
                pins = [getObjectFromCatalog(catalog, rid) for rid in cluster_rids]
                return self.cluster_index(pins=pins)

            num_points = len(cluster['points'])
            if num_points == 1:
                point = cluster['points'][0]
                pin = getObjectFromCatalog(catalog, r_list[point.id])
                icon_name = 'mk_single_rating_%s_%d' % (pin.type, pin.rating)

                return {'id': pin.id,
                        'icon_name': icon_name,
                        'lat': pin.latitude,
                        'lon': pin.longitude,
                        'display_tooltip': False,
                        'tooltip': '',
                        'label': ''}
            else:
                rating = int(cluster['averageRating'])

                display_tooltip = (lat_max - lat_min) < 1.
                if display_tooltip:
                    tooltip = cluster_tooltip(cluster, r_list)
                else:
                    tooltip = ''
                icon_name = 'mk_rating_%s_%d_%d' % (cluster['type'],
                                                    rating,
                                                    num_points)
                return {'id': '',
                        'icon_name': icon_name,
                        'lat': cluster['center'].lat,
                        'lon': cluster['center'].lon,
                        'display_tooltip': display_tooltip,
                        'tooltip': tooltip,
                        'label': 'cluster',
                        'num_points': num_points}

        tc_start = time()
        lat_min, lat_max = float(lat_min), float(lat_max)
        lon_min, lon_max = float(lon_min), float(lon_max)

        grid_size = 7
        tlat_min, tlat_max, tlon_min, tlon_max = get_discretized_limits(
            lat_min, lat_max, lon_min, lon_max, grid_size)

        catalog = self.context.catalog

        tc_start_apply_idxs = time()
        type_dict = get_index_dict('type', catalog)
        lat_dict = get_index_dict('latitude', catalog, tlat_min, tlat_max)
        lon_dict = get_index_dict('longitude', catalog, tlon_min, tlon_max)
        rating_dict = get_index_dict('rating', catalog)
        tc_end_apply_idxs = time()
        print 'apply indexes', tc_end_apply_idxs - tc_start_apply_idxs

        map_filters = {'latitude': {'query': (tlat_min, tlat_max),
                                    'range': 'min:max'},
                       'longitude': {'query': (tlon_min, tlon_max),
                                     'range': 'min:max'}}
        rids = filter_rids(catalog, map_filters)
        if rids is None:
            r_list = []
        else:
            r_list = list(set(rids))

        points = make_points(r_list, lat_dict, lon_dict, type_dict, rating_dict)
        points_by_type = make_points_by_type(points)
        clusters = make_clusters(points_by_type, tlat_min, tlat_max,
                                 tlon_min, tlon_max, grid_size)
        points = [point_data(cluster, r_list) for cluster in clusters]
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
        return short_string(s, limit)

    def check_user_can_add_pin(self, lat, lon, author, session_key):
        """ """
        tc_start = time()
        catalog = self.context.catalog

        # modify if map_distance limit changes
        lat_min, lat_max = lat - 5., lat + 5.
        # lon distances differ with latitude (but for performance)
        lon_min, lon_max = lon - 20., lon + 20.
        date_min, date_max = datetime.now() - timedelta(weeks=1), datetime.now()

        filters = {'latitude': {'query': (lat_min, lat_max),
                                'range': 'min:max'},
                   'longitude': {'query': (lon_min, lon_max),
                                 'range': 'min:max'},
                   'date': {'query': (date_min, date_max),
                            'range': 'min:max'},
                   'author': author,
                   'session_key': session_key}

        rids = filter_rids(catalog, filters)
        if rids is None:
            r_list = []
        else:
            r_list = list(set(rids))

        tc_start_apply_idxs = time()
        lat_dict = get_index_dict('latitude', catalog, lat_min, lat_max)
        lon_dict = get_index_dict('longitude', catalog, lon_min, lon_max)
        tc_end_apply_idxs = time()
        print 'apply indexes', tc_end_apply_idxs - tc_start_apply_idxs

        ret = True
        for rid in r_list:
            clat, clon = lat_dict[rid], lon_dict[rid]
            if map_distance(lat, lon, clat, clon) < 1: #km
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

    cluster_index = ViewPageTemplateFile('zpt/cluster_index.zpt', globals())

    def country_statistics(self, country):
        catalog = self.context.catalog
        tc_start_apply_idxs = time()
        country_dict = get_index_dict('country', catalog, country, country)
        type_dict = get_index_dict('type', catalog)
        rating_dict = get_index_dict('rating', catalog)
        tc_end_apply_idxs = time()
        print 'apply indexes', tc_end_apply_idxs - tc_start_apply_idxs

        statistics = {}
        for type in TYPE_VALUES:
            ratings = [rating_dict[rid] for rid in country_dict.keys()
                                            if type_dict[rid] == type]
            type_stats = {'num_ratings': len(ratings)}
            if len(ratings) > 0:
                average_rating = sum(ratings) / float(len(ratings))
                type_stats['average_rating'] = average_rating
            statistics[type] = type_stats
        return statistics

    def get_countries(self, q):
        """ """
        def country_matches(country, q):
            return country.lower().startswith(q.lower())

        catalog = self.context.catalog
        country_dict = get_index_dict('country', catalog)
        country_set = set(country_dict.values())
        return '\n'.join([country for country in country_set
                                    if country_matches(country, q)])

    def observamap_i18n_js(self):
        """ """
        return ''

