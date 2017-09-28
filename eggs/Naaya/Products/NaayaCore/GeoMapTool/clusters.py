import math

class Point:
    def __init__(self, id=-1, lat=0., lon=0.):
        self.id = id
        self.lat = lat
        self.lon = lon
    def __repr__(self):
        return '<Point id=%s lat=%s, lon=%s>' % (self.id, self.lat, self.lon)

def getFullGridSize(size_y, size_x, lat_min, lat_max, lon_min, lon_max):
    """ get the size of the full map grid based on the sizes for the view """
    return (
            int(math.floor(size_y * (360. / abs(lon_max - lon_min)))),#d(lat) is not constant
            int(math.floor(size_x * (360. / abs(lon_max - lon_min)))),
            # please note d(lon) not 100% of time constant - google maps inconsistency
            )

def y_from_lat(size_y, lat):
    return (lat + 90.) * size_y / 180.

def x_from_lon(size_x, lon):
    return (lon + 180.) * size_x / 360.

def tile_limits(size_y, size_x, lat_min, lat_max, lon_min, lon_max):
    return (
            int(math.floor(y_from_lat(size_y, lat_min))),
            int(math.ceil(y_from_lat(size_y, lat_max))),
            int(math.floor(x_from_lon(size_x, lon_min))),
            int(math.ceil(x_from_lon(size_x, lon_max))),
            )

def get_tile(size_y, size_x, lat, lon):
    """Given lat and lon, return bounding tile (ty, tx)"""
    return (
            int(math.floor(y_from_lat(size_y, lat))),
            int(math.floor(x_from_lon(size_x, lon)))
           )

def getLatLonFromTile(size_y, size_x, y, x, dy=0., dx=0.):
    """ Returns the lat and lon of the point with dx,dy inside x,y tile
    where 0. <= dx <= 1. and 0. <= dy <= 1. (selects the actual point in tile)
    """

    lat = 180. * (y + dy) / size_y - 90.
    lon = 360. * (x + dx) / size_x - 180.

    return lat, lon

def calc_centers(lat_min, lat_max, lon_min, lon_max, size_x,
                 size_y, points):
    ty_min, ty_max, tx_min, tx_max = tile_limits(size_y, size_x,
                                        lat_min, lat_max, lon_min, lon_max)
    groups = {}
    centers = []

    for p in points:
        (y, x) = get_tile(size_y, size_x, p.lat, p.lon)
        assert tx_min <= x < tx_max
        assert ty_min <= y < ty_max
        group_p = groups.setdefault( (y, x), [] )
        group_p.append(p)

    final_groups = groups.values()
    for group in final_groups:
        lat = sum(p.lat for p in group) / len(group)
        lon = sum(p.lon for p in group) / len(group)
        centers.append(Point(-1, lat, lon))
    return centers, final_groups

def kmeans(lat_min, lat_max, lon_min, lon_max, points, size_x, size_y=None):
    """
    size_x, size_y - are the dimensions of the initial grid of centers on full map
    """
    # default arguments for size_y and centers_step
    if size_y is None:
        size_y = size_x

    size_y, size_x = getFullGridSize(size_y, size_x, lat_min, lat_max, lon_min, lon_max)

    return calc_centers(lat_min, lat_max, lon_min, lon_max,
                      size_x, size_y, points)

def get_discretized_limits(lat_min, lat_max, lon_min, lon_max,
        size_x, size_y=None):
    """
    Returns the tile limits that cover the map borders
     Used for expanding limits to include whole margin tile,
     in order to find results
     also right outside the margins, maintaining the same clusters
     on map movements
    """
    # default arguments for size_y and centers_step
    if size_y is None:
        size_y = size_x

    size_y, size_x = getFullGridSize(size_y, size_x, lat_min, lat_max, lon_min, lon_max)

    ty_min, ty_max, tx_min, tx_max = tile_limits(size_y, size_x,
                                        lat_min, lat_max, lon_min, lon_max)

    # get lat, lon for the margins
    tlat_min, tlon_min = getLatLonFromTile(size_y, size_x, ty_min, tx_min, 0., 0.)
    tlat_max, tlon_max = getLatLonFromTile(size_y, size_x, ty_max, tx_max, 0., 0.)

    return (tlat_min, tlat_max, tlon_min, tlon_max)
