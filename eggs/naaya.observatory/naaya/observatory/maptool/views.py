import simplejson as json
from random import randint
from time import time
from StringIO import StringIO
import os

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

from pin import addPushPin, removePushPin, PushPin, ratePushPin, removeRating

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

    def get_pin_tooltip(self, pin):
        pin_view = self.site.unrestrictedTraverse(pin.absolute_url(1) + '/observatory_rating_comments_view')
        return pin_view()

    def map_new_point(self, latitude, longitude):
        view = self.site.unrestrictedTraverse(self.site.absolute_url(1) + '/observatory_map_new_point')
        return view(latitude=latitude, longitude=longitude)

    def address(self, lat, lon):
        try:
            return reverse_geocode(lat, lon)
        except GeocoderServiceError, e:
            zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
            return ''

    def map_image(self, number, rating, RESPONSE):
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
        rating_idx = catalog._catalog.indexes['averageRating']
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
                icon_name = 'mk_single_rating_%d' % ob.averageRating
                return {'lon': ob.longitude,
                        'lat': ob.latitude,
                        'tooltip': self.get_pin_tooltip(ob),
                        'label': '',
                        'icon_name': icon_name,
                        'id': ob.id}
            else:
                rating = int(3*ob.averageRating)
                icon_name = 'mk_rating_%d_%d' % (rating, len(ob.group))
                return {'lon': ob.lon,
                        'lat': ob.lat,
                        'tooltip': self.get_tooltip(ob),
                        'label': 'cluster',
                        'icon_name': icon_name,
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
                    'url': 'observatory_map_image?rating=%s&number=%s' % (i+1, j),
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
        """ render the HTML needed to set up the current map engine """
        global_config = {
            'initial_address': self.portal_map.initial_address,
            'icons': list(self.get_geotype_icons()),
        }
        global_config.update(kwargs)
        map_engine = self.portal_map.get_map_engine()
        return map_engine.html_setup(request, global_config)

    def reset_observatory(self):
        current_observatory = self.site._getOb('observatory', None)
        if current_observatory is not None:
            self.site._delOb('observatory')
        self.site._setOb('observatory', BTreeFolder2(id='observatory'))
        parent = self.site.observatory
        manage_addZCatalog(parent, 'catalog', '')
        catalog = parent.catalog
        manage_addFieldIndex(catalog, 'averageRating')
        manage_addFieldIndex(catalog, 'latitude')
        manage_addFieldIndex(catalog, 'longitude')
        manage_addFieldIndex(catalog, 'id_pin')

    def add_pin_to_observatory(self, lat, lon, type, rating):
        """ """
        lat, lon = float(lat), float(lon)
        rating = int(rating)

        assert -90 < lat < 90
        assert -180 < lon < 180
        assert rating in RATING_VALUES
        assert type in TYPE_VALUES

        parent = self.site.observatory
        pin_index = addPushPin(parent, parent.catalog, lat, lon)
        ratePushPin(parent, parent.catalog, pin_index, type, rating)

    def add_objects_to_observatory(self):
        parent = self.site.observatory
        for i in range(20*1000):
            latitude = randint(-89, 89)
            longitude = randint(-179, 179)
            addPushPin(parent, parent.catalog, latitude, longitude)

        for i in range(20*1000):
            pin_index = randint(0, 20*1000-1)
            type = randint(0, 2)
            rating = 1 + i % 5
            ratePushPin(parent, parent.catalog, pin_index, type, rating)

    def remove_objects_from_observatory(self):
        parent = self.site.observatory
        for i in range(20*1000):
            removeRating(parent, parent.catalog, i)

        for i in range(20*1000):
            removePushPin(parent, parent.catalog, i)

    def view_objects_in_observatory(self):
        catalog = self.site.observatory.catalog

        rating_idx = catalog._catalog.indexes['averageRating']
        def queryRating(rating):
            return rating_idx._apply_index({'averageRating': {'query': rating}})

        lat_idx = catalog._catalog.indexes['latitude']
        def queryLat(lat_min, lat_max):
            return lat_idx._apply_index({'latitude': {'query': (lat_min, lat_max), 'range': 'min:max'}})

        lon_idx = catalog._catalog.indexes['longitude']
        def queryLon(lon_min, lon_max):
            return lon_idx._apply_index({'longitude': {'query': (lon_min, lon_max), 'range': 'min:max'}})

        def filter(lat_min, lat_max, lon_min, lon_max):
            t_start = time()
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

            lat_set, lat_dict = _apply_index_with_range_dict_results(lat_idx._index, lat_min, lat_max)
            lon_set, lon_dict = _apply_index_with_range_dict_results(lon_idx._index, lon_min, lon_max)

            t_end = time()

            return rs_f, lat_dict, lon_dict, t_end - t_start

        import pdb; pdb.set_trace()
        pass


