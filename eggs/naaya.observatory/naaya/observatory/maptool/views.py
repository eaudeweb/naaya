import simplejson as json
from random import randint, choice
from time import time
from StringIO import StringIO
import os
from datetime import datetime

from PIL import Image

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import manage_addFieldIndex
from BTrees.IIBTree import IISet, union, weightedIntersection
from App.Common import rfc1123_date
import zLOG

from Products.NaayaCore.GeoMapTool.clusters_catalog import _apply_index_with_range_dict_results, getObjectFromCatalog
from Products.NaayaCore.GeoMapTool import clusters
from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

from naaya.observatory.contentratings.views import RATING_IMAGE_PATHS as SINGLE_RATING_IMAGE_PATHS
from naaya.observatory.contentratings.views import TYPE_IMAGE_PATHS

RESOURCES_PATH = '++resource++naaya.observatory.maptool'
IMAGES_PATH = RESOURCES_PATH + '/images'

RATING_IMAGE_NAMES = range(1, 15+1)
RATING_IMAGE_PATHS = ['%s/rating_%s.png' % (IMAGES_PATH, f)
                        for f in RATING_IMAGE_NAMES]

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

    def address(self, lat, lon):
        try:
            return reverse_geocode(lat, lon)
        except GeocoderServiceError, e:
            zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
            return ''

    def map_icon(self, number, rating, RESPONSE):
        number = int(number)
        rating = int(rating)
        current_dir = os.path.dirname(__file__)

        def apply(main_icon, icons):
            layer = Image.new('RGBA', main_icon.size, (0,0,0,0))
            xs = [icon.size[0] for icon in icons]
            ys = [icon.size[1] for icon in icons]

            xm, ym = main_icon.size

            dx = (xm - sum(xs)) / 2 # where the first icon starts
            dy = ym - 5 # where the icon ends

            for i, icon in enumerate(icons):
                x = dx + sum(xs[:i])
                y = dy - ys[i]
                assert x >= 0 and y >= 0
                layer.paste(icon, (x, y))

            return layer

        pin_icon = Image.open('%s/www/images/rating_%d.png' %
                (current_dir, rating))

        if number < 1000:
            digits = [int(ds) for ds in str(number)]
            icon_names = ['%d.png' % d for d in digits]
        else:
            icon_names = ['gt.png', '1.png', 'k.png']

        icon_paths = ['%s/www/images/%s' % (current_dir, icon_name)
                for icon_name in icon_names]
        icons = [Image.open(icon_path) for icon_path in icon_paths]
        layer = apply(pin_icon, icons)
        result_image = Image.composite(layer, pin_icon, layer)

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

        def make_points():
            lat_set, lat_dict = _apply_index_with_range_dict_results(lat_idx._index, lat_min, lat_max)
            lon_set, lon_dict = _apply_index_with_range_dict_results(lon_idx._index, lon_min, lon_max)

            # transform objects to points
            points = []
            for i, rid in enumerate(rids):
                points.append(clusters.Point(i, float(lat_dict[rid]), float(lon_dict[rid])))
            return points
        points = make_points()

        def make_centers():
            centers, groups = clusters.kmeans(lat_min, lat_max, lon_min, lon_max, points, 10)
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
            return centers
        centers = make_centers()

        def build_point(ob):
            if len(ob.group) == 1:
                rid = rids[ob.group[0].id]
                ob = getObjectFromCatalog(catalog, rid)
                icon_name = 'mk_single_rating_%d' % ob.rating
                return {'lon': ob.longitude,
                        'lat': ob.latitude,
                        'tooltip': '', #self.get_pin_tooltip(ob),
                        'label': '',
                        'icon_name': icon_name,
                        'id': ob.id}
            else:
                rating = int(3*ob.averageRating)
                icon_name = 'mk_rating_%d_%d' % (rating, len(ob.group))
                return {'lon': ob.lon,
                        'lat': ob.lat,
                        'tooltip': '', #self.get_tooltip(ob),
                        'label': 'cluster',
                        'icon_name': icon_name,
                        'num_points': len(ob.group),
                        'id': ob.id}

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
        for i, img_path in enumerate(RATING_IMAGE_PATHS):
            for j in range(999):
                yield {
                    'id': "rating_%d_%d" % (i+1, j),
                    'url': 'observatory_map_icon?rating=%s&number=%s' % (i+1, j),
                    'w': 38,
                    'h': 37,
                }

        # single objects images
        for i, img_path in enumerate(SINGLE_RATING_IMAGE_PATHS):
            yield {
                    'id': "single_rating_%d" % (i+1),
                    'url': img_path,
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
        map_engine = self.portal_map.engine_bing
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


    def add_pin_to_observatory(self, lat, lon, address, type, rating, REQUEST,
            comment=None):
        """ """
        lat, lon = float(lat), float(lon)
        rating = int(rating)
        date = datetime.now()
        author, session_key = self.get_author_and_session(REQUEST)

        observatory = self.site.observatory
        pin_index = observatory.add_pin(type, lat, lon, address,
                rating, comment, date, author, session_key)

    def add_random_pins_to_observatory(self, num, REQUEST):
        num = int(num)
        observatory = self.site.observatory
        for i in range(num):
            lat, lon = randint(-89, 89), randint(-179, 179)
            type = choice(TYPE_VALUES)
            rating = choice(RATING_VALUES)
            observatory.add_pin_to_observatory(lat, lon, '', type, rating,
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
        return SINGLE_RATING_IMAGE_PATHS[rating-1]

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

