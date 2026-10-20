from decimal import Decimal

from BTrees.IIBTree import IISet
from BTrees.IIBTree import multiunion
from BTrees.IIBTree import intersection

from Products.NaayaCore.GeoMapTool import clusters

# used by naaya.observatory
def _apply_index_with_range_dict_results(index, low_value=None, high_value=None):
    """ return an IISet of the rids matching the range in the index
        also return a dict matching each rid to the value of the index for that rid
    """
    index_items = index.items(low_value, high_value)

    r_set = []
    r_dict = dict()

    for k, kset in index_items:
        if isinstance(kset, int):
            r_dict[kset] = k
            r_set.append(kset)
        else:
            r_set.extend(kset)
            for kitem in kset:
                r_dict[kitem] = k

    r_set = multiunion(r_set) if r_set else IISet()

    return r_set, r_dict

def getObjectPathFromCatalog(catalog_tool, rid):
    portal_path = '/'.join(catalog_tool.getSite().getPhysicalPath())
    return catalog_tool._catalog.getpath(rid)[len(portal_path)+1:]

def getObjectFromCatalog(catalog_tool, rid):
    """ get the object from the rid using the catalog_tool """
    obj_path = catalog_tool._catalog.getpath(rid)
    object = catalog_tool._catalog.unrestrictedTraverse(obj_path)
    return object

def getClusters(catalog_tool, filters):
    # the objects are searched for in the tile limits (to get the same clusters every time)
    grid_size = 16 # geopoints' and clusters' density on map / also depends on map frame size

    # unpack map limits
    if filters:
        lat_min = float(filters[0]['geo_latitude']['query'][0])
        lat_max = float(filters[0]['geo_latitude']['query'][1])

        lon_min = float(filters[0]['geo_longitude']['query'][0])
        lon_max = float(filters[0]['geo_longitude']['query'][1])
    else: # this should not happen
        return [], []

    tlat_min, tlat_max, tlon_min, tlon_max = clusters.get_discretized_limits(lat_min, lat_max, lon_min, lon_max, grid_size)

    catalog = catalog_tool._catalog

    # rid -> coordinate; a range over the _index loads one set per distinct coordinate
    lat_values = catalog.getIndex('geo_latitude')._unindex
    lon_values = catalog.getIndex('geo_longitude')._unindex

    d_tlat_min = Decimal(str(tlat_min))
    d_tlat_max = Decimal(str(tlat_max))
    d_tlon_min = Decimal(str(tlon_min))
    d_tlon_max = Decimal(str(tlon_max))

    # OR the filters, each one the intersection of its other indexes
    rs_final = []
    for f in filters:
        rs_f = None
        for idx_name in f:
            if idx_name in ('geo_latitude', 'geo_longitude'):
                continue
            index = catalog.getIndex(idx_name)
            if not hasattr(index, '_apply_index'):
                # Skip broken indexes (e.g. TextIndex removed in Zope 5)
                continue
            r = index._apply_index(f)
            if r is not None:
                r, _ = r
                rs_f = intersection(rs_f, r)
        if rs_f is None:
            rs_f = IISet(lat_values.keys())
        rs_final.append(rs_f)

    # points inside the discretized tile limits
    r_list = []
    points = []
    for rid in multiunion(rs_final):
        lat = lat_values.get(rid)
        lon = lon_values.get(rid)
        if lat is None or lon is None:
            continue
        if d_tlat_min <= lat <= d_tlat_max and d_tlon_min <= lon <= d_tlon_max:
            points.append(clusters.Point(len(r_list), float(lat), float(lon)))
            r_list.append(rid)

    centers, groups = clusters.kmeans(tlat_min, tlat_max, tlon_min, tlon_max, points, grid_size)

    # transform group points to rids
    for i in range(len(groups)):
        groups[i] = list(map(lambda p: r_list[p.id], groups[i]))

    return centers, groups
