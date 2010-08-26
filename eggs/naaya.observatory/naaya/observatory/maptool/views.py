import simplejson as json
from random import randint, choice
from time import time
from StringIO import StringIO
import os
from datetime import datetime, timedelta

from PIL import Image

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import manage_addFieldIndex
from BTrees.IIBTree import IISet, union, weightedIntersection
from App.Common import rfc1123_date
import zLOG
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.GeoMapTool.clusters_catalog import _apply_index_with_range_dict_results, getObjectFromCatalog
from Products.NaayaCore.GeoMapTool import clusters
from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

RESOURCES_PATH = '++resource++naaya.observatory.maptool'
IMAGES_PATH = RESOURCES_PATH + '/images'

RATING_IMAGE_NAMES = ['very-bad', 'bad', 'average', 'good', 'very-good']
RATING_IMAGE_PATHS = ['%s/%s.png' % (IMAGES_PATH, f)
                        for f in RATING_IMAGE_NAMES]

TYPE_IMAGE_NAMES = ['vegetation', 'water', 'soil', 'citizens']
TYPE_IMAGE_PATHS = ['%s/%s.png' % (IMAGES_PATH, f)
                    for f in TYPE_IMAGE_NAMES]

RATING_VALUES = range(1, 5+1)
TYPE_VALUES = ['veg', 'wat', 'soil', 'cit']

class MapView(object):
    """A view for the observatory map"""

    def __init__(self, context, request):
        self.context = context
        self.site = context.getSite()
        self.request = request
        self.portal_map = context.getGeoMapTool()

    def get_tooltip(self, ob):
        return """
        <div class="marker-body">
            <small></small>
            <div class="marker-more">
                <div>Average rating: %s</div>
            </div>
        </div>
        """ % ob.averageRating

    def reverse_geocode(self, lat, lon):
        try:
            return reverse_geocode(lat, lon)
        except GeocoderServiceError, e:
            zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
            return '', ''

    def map_icon(self, rating, type, RESPONSE, number=None):
        rating = int(rating)
        assert type in TYPE_VALUES
        assert rating in RATING_VALUES
        if number is not None:
            number = int(number)

        def apply(rating_icon, type_icon, number_icons=None):
            layer = Image.new('RGBA', rating_icon.size, (0,0,0,0))
            xr, yr = rating_icon.size

            # add type layer
            xt, yt = type_icon.size
            x, y = (xr - xt) / 2, (yr - yt) / 2 - 3
            layer.paste(type_icon, (x, y))

            if number_icons is None:
                return layer

            # add number layer
            xns = [icon.size[0] for icon in number_icons]
            yns = [icon.size[1] for icon in number_icons]

            dx = (xr - sum(xns)) / 2 # where the first icon starts
            dy = yr - 3 # where the icon ends

            for i, icon in enumerate(number_icons):
                x = dx + sum(xns[:i])
                y = dy - yns[i]
                assert x >= 0 and y >= 0
                layer.paste(icon, (x, y))

            return layer

        current_dir = os.path.dirname(__file__)
        RATING_FILENAMES = ['very-bad_map.png', 'bad_map.png',
                'average_map.png', 'good_map.png', 'very-good_map.png']
        rating_filename = RATING_FILENAMES[rating-1]
        if type == 'cit' and number is not None:
            rating_filename = 'gray.png'
        rating_icon = Image.open('%s/www/images/%s' %
                (current_dir, rating_filename))

        TYPE_FILENAMES = {'veg': 'vegetation_map.png', 'wat': 'water_map.png',
                'soil': 'soil_map.png', 'cit': 'citizens_map.png'}
        type_filename = TYPE_FILENAMES[type]
        type_icon = Image.open('%s/www/images/%s' %
                (current_dir, type_filename))

        if number is not None:
            if number < 1000:
                digits = [int(ds) for ds in str(number)]
                number_icon_names = ['no%d.png' % d for d in digits]
            else:
                number_icon_names = ['more.png', 'no1.png', 'k.png']
            number_icon_paths = ['%s/www/images/%s' % (current_dir, icon_name)
                                for icon_name in number_icon_names]
            number_icons = [Image.open(icon_path)
                                for icon_path in number_icon_paths]
        else:
            number_icons = None
        layer = apply(rating_icon, type_icon, number_icons)
        result_image = Image.composite(layer, rating_icon, layer)

        out_str = StringIO()
        result_image.save(out_str, 'PNG')
        ret = out_str.getvalue()
        out_str.close()

        RESPONSE.setHeader('Content-Type', 'image/png')
        RESPONSE.setHeader('Cache-Control', 'public,max-age=86400')
        RESPONSE.setHeader('Expires', rfc1123_date(time() + 86400))

        return ret

    def xrjs_getClusters(self, lat_min, lat_max, lon_min, lon_max):
        """ """
        tc_start = time()
        lat_min, lat_max = float(lat_min), float(lat_max)
        lon_min, lon_max = float(lon_min), float(lon_max)

        catalog = self.site.observatory.catalog
        rating_idx = catalog._catalog.indexes['rating']

        lat_idx = catalog._catalog.indexes['latitude']
        lon_idx = catalog._catalog.indexes['longitude']
        lat_set, lat_dict = _apply_index_with_range_dict_results(lat_idx._index, lat_min, lat_max)
        lon_set, lon_dict = _apply_index_with_range_dict_results(lon_idx._index, lon_min, lon_max)

        type_idx = catalog._catalog.indexes['type']
        tyle_set, type_dict = _apply_index_with_range_dict_results(type_idx._index)

        tc_start_id_idx = time()
        id_idx = catalog._catalog.indexes['id']
        id_set, id_dict = _apply_index_with_range_dict_results(id_idx._index)
        tc_end_id_idx = time()
        print 'id_idx', tc_end_id_idx - tc_start_id_idx

        def filter_rids():
            f = {'latitude': {'query': (lat_min, lat_max),
                              'range': 'min:max'},
                 'longitude': {'query': (lon_min, lon_max),
                               'range': 'min:max'}}

            r_lat = lat_idx._apply_index(f)
            if r_lat is not None:
                r_lat = r_lat[0]
            r_lon = lon_idx._apply_index(f)
            if r_lon is not None:
                r_lon = r_lon[0]

            if r_lat is not None and r_lon is not None:
                w, rs_f = weightedIntersection(r_lat, r_lon)
            else:
                rs_f = None
            return list(set(rs_f))
        rids = filter_rids()

        def make_points_by_type():

            # transform objects to points
            points_by_type = {}
            for i, rid in enumerate(rids):
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

                centers, groups = clusters.kmeans(lat_min, lat_max, lon_min, lon_max, points, 7)

                # get ratings for centers
                rating_set, rating_dict = _apply_index_with_range_dict_results(rating_idx._index)
                for i, g in enumerate(groups):
                    l_rat = []
                    for p in g:
                        p_rat = rating_dict[rids[p.id]]
                        if p_rat is not None:
                            l_rat.append(rating_dict[rids[p.id]])
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
            lis = []
            for p in ob.group:
                id = id_dict[rids[p.id]]
                lat, lon = lat_dict[rids[p.id]], lon_dict[rids[p.id]]
                js = 'view_point(%s, %s, \'%s\')' % (lat, lon, id)
                lis.append('<li><a onclick="%s">Point %s</a></li>'
                                % (js, id))
            if len(lis) == 0:
                return ''
            lis_str = '\n'.join(lis)
            return '<ul>%s</ul>' % lis_str

        def build_point(ob):
            if len(ob.group) == 1:
                rid = rids[ob.group[0].id]
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
                icon_name = 'mk_rating_%s_%d_%d' % (ob.type, rating, len(ob.group))
                return {'lon': ob.lon,
                        'lat': ob.lat,
                        'tooltip': tooltip,
                        'display_tooltip': display_tooltip,
                        'label': 'cluster',
                        'icon_name': icon_name,
                        'num_points': len(ob.group),
                        'id': ''}

        points = [build_point(c) for c in centers if c.averageRating]
        tc_end = time()
        print 'clusters', tc_end - tc_start
        return json.dumps({'points': points})

    def xrjs_getTooltip(self):
        """ """
        my_ob = self.site.info.accessibility
        my_view = self.site.unrestrictedTraverse(my_ob.absolute_url(1) + '/observatory_rating_comments_view')
        return my_view()

    def get_geotype_icons(self):
        # cluster images
        for rating in RATING_VALUES:
            for type in TYPE_VALUES:
                for count in range(1000+1):
                    id = 'rating_%s_%d_%d' % (type, rating, count)
                    url = ('observatory_map_icon?type=%s&rating=%s&number=%s'
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
                url = ('observatory_map_icon?type=%s&rating=%s'
                                % (type, rating))
                yield {
                        'id': id,
                        'url': url,
                        'w': 38,
                        'h': 37,
                }

    def setup_map_engine_html(self, request, **kwargs):
        """ render the HTML needed to set up the bing map engine """
        assert hasattr(self.portal_map, 'engine_bing')

        global_config = {
            'initial_address': self.portal_map.initial_address,
            'icons': list(self.get_geotype_icons()),
        }
        global_config.update(kwargs)
        map_engine = self.portal_map.get_map_engine()
        return map_engine.html_setup(request, global_config)


    SESSION_KEY = '__naaya_observatory_session'
    def generate_session_key(self):
        return randint(10**5, 10**10)

    def get_author_and_session(self, REQUEST):
        author = REQUEST.AUTHENTICATED_USER.getUserName()
        if author == 'Anonymous User':
            session_key = REQUEST.cookies.get(self.SESSION_KEY, None)
            if session_key == None:
                session_key = self.generate_session_key()
                REQUEST.RESPONSE.setCookie(self.SESSION_KEY, session_key)
        else:
            session_key = None
        return author, session_key

    def query_author_and_session(self, REQUEST):
        author = REQUEST.AUTHENTICATED_USER.getUserName()
        if author == 'Anonymous User':
            session_key = REQUEST.cookies.get(self.SESSION_KEY, None)
        else:
            session_key = None
        return author, session_key


    def add_pin_to_observatory(self, lat, lon, address, country, type, rating,
            REQUEST, comment=None):
        """ """
        lat, lon = float(lat), float(lon)
        rating = int(rating)
        date = datetime.now()
        author, session_key = self.get_author_and_session(REQUEST)

        observatory = self.site.observatory
        pin_index = observatory.add_pin(type, lat, lon, address, country,
                rating, comment, date, author, session_key)

    def add_random_pins_to_observatory(self, num, REQUEST):
        num = int(num)
        observatory = self.site.observatory
        for i in range(num):
            lat = randint(-89*100, 89*100)/100.
            lon = randint(-179*100, 179*100)/100.
            type = choice(TYPE_VALUES)
            rating = choice(RATING_VALUES)
            observatory.add_pin_to_observatory(lat, lon, '', '', type, rating,
                    REQUEST)

    def get_pin_by_id(self, id):
        observatory = self.site.observatory
        return observatory.get_pin(id)

    def type_image_paths(self, type):
        index = TYPE_VALUES.index(type)
        return TYPE_IMAGE_PATHS[index]

    TYPE_MESSAGES = ['Vegetation', 'Water', 'Soil', 'Citizen reported']
    def type_messages(self, type):
        translations_tool = self.context.getPortalTranslations()
        index = TYPE_VALUES.index(type)
        return translations_tool(self.TYPE_MESSAGES[index])

    def rating_image_paths(self, rating):
        return RATING_IMAGE_PATHS[rating-1]

    RATING_MESSAGES = ['Very bad', 'Bad', 'Average', 'Good', 'Very good']
    def rating_messages(self, rating):
        translations_tool = self.site.getPortalTranslations()
        return translations_tool(self.RATING_MESSAGES[rating-1])

    RATING_TITLES = ['Vote %s' % l for l in RATING_MESSAGES]
    def rating_titles(self, rating):
        translations_tool = self.site.getPortalTranslations()
        return translations_tool(self.RATING_TITLES[rating-1])

    RATING_ALTS = list(RATING_MESSAGES)
    def rating_alts(self, rating):
        translations_tool = self.site.getPortalTranslations()
        return translations_tool(self.RATING_ALTS[rating-1])

    def map_distance(self, lats, lons, latf, lonf):
        import math
        def deg_to_rad(deg):
            return deg * math.pi / 180
        fis, lams = deg_to_rad(lats), deg_to_rad(lons)
        fif, lamf = deg_to_rad(latf), deg_to_rad(lonf)
        dfi, dlam = math.fabs(fis - fif), math.fabs(lams - lamf)
        dang = math.acos(math.sin(fis) * math.sin(fif) +
                math.cos(fis) * math.cos(fif) * math.cos(dlam))
        earth_radius = 6371 # in km
        return earth_radius * dang

    def check_user_can_add_pin(self, lat, lon, author, session_key):
        """ """
        tc_start = time()
        observatory = self.site.observatory
        catalog = observatory.catalog
        def filter_rids():
            f = {'author': author,
                 'session_key': session_key}

            author_idx = catalog._catalog.indexes['author']
            session_idx = catalog._catalog.indexes['session_key']

            r_author = author_idx._apply_index(f)
            if r_author is not None:
                r_author = r_author[0]
            r_session = session_idx._apply_index(f)
            if r_session is not None:
                r_session = r_session[0]

            if r_author is not None and r_session is not None:
                w, rs_f = weightedIntersection(r_author, r_session)
            else:
                rs_f = None
            return list(set(rs_f))

        rids = filter_rids()
        tc_filter = time()

        lat_idx = catalog._catalog.indexes['latitude']
        lon_idx = catalog._catalog.indexes['longitude']
        date_idx = catalog._catalog.indexes['date']

        _, lat_dict = _apply_index_with_range_dict_results(lat_idx._index)
        _, lon_dict = _apply_index_with_range_dict_results(lon_idx._index)
        _, date_dict = _apply_index_with_range_dict_results(date_idx._index)

        def convert_to_datetime(date_index_val):
            year = date_index_val / 535680
            month = (date_index_val / 44640) % 12
            day = (date_index_val / 1440) % 31
            hour = (date_index_val / 60) % 24
            minute = date_index_val % 60
            return datetime(year, month, day, hour, minute)

        ret = True
        for rid in rids:
            clat, clon = lat_dict[rid], lon_dict[rid]
            if self.map_distance(lat, lon, clat, clon) < 1: #km
                cdate = convert_to_datetime(date_dict[rid])
                if datetime.now() - cdate < timedelta(weeks=1):
                    ret = False
                    break
        tc_end = time()
        print 'check user can add pin', tc_end - tc_start
        return ret

    _pin_add = PageTemplateFile('zpt/pin_add', globals())
    def pin_add(self, latitude, longitude, REQUEST, type=None):
        """ """
        lat, lon = float(latitude), float(longitude)
        author, session_key = self.query_author_and_session(REQUEST)
        can_add = self.check_user_can_add_pin(lat, lon, author, session_key)

        if not can_add:
            return json.dumps({'can_add': can_add})

        address, country = self.reverse_geocode(lat, lon)
        html = self._pin_add.__of__(self.context)(latitude=latitude,
                                                  longitude=longitude,
                                                  address=address,
                                                  country=country,
                                                  type=type)
        return json.dumps({'can_add': can_add, 'html': html})

    _cluster_index = PageTemplateFile('zpt/cluster_index', globals())
    def cluster_index(self, point_ids, REQUEST):
        """ """

        return self._cluster_index.__of__(self.context)(points=points)

