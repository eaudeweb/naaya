import os
from StringIO import StringIO
import math

from PIL import Image

import zLOG

from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

from observatory import TYPE_VALUES, RATING_VALUES

def query_reverse_geocode(lat, lon):
    """ calls reverse_geocode and logs the error """
    try:
        return reverse_geocode(lat, lon)
    except GeocoderServiceError, e:
        zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
        return '', ''

def map_icon(rating, type, number=None):
    """ combines the rating, type and number images """
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
        if number_icons is None:
            x, y = (xr - xt) / 2, (yr - yt) / 2
            layer.paste(type_icon, (x, y))
            return layer
        else:
            x, y = (xr - xt) / 2, (yr - yt) / 2 - 3
            layer.paste(type_icon, (x, y))

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

    return ret


def map_distance(lats, lons, latf, lonf):
    """ returns distance in km """
    def deg_to_rad(deg):
        return deg * math.pi / 180
    fis, lams = deg_to_rad(lats), deg_to_rad(lons)
    fif, lamf = deg_to_rad(latf), deg_to_rad(lonf)
    dfi, dlam = math.fabs(fis - fif), math.fabs(lams - lamf)
    dang = math.acos(math.sin(fis) * math.sin(fif) +
            math.cos(fis) * math.cos(fif) * math.cos(dlam))
    earth_radius = 6371 # in km
    return earth_radius * dang


def short_string(s, limit):
    if len(s) <= limit:
        return s
    return s[:limit-3] + '...'

