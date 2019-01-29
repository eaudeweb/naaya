from decimal import Decimal

from BTrees.IIBTree import IISet
from BTrees.IIBTree import multiunion
from BTrees.IIBTree import intersection

from Products.NaayaCore.GeoMapTool import clusters

# this is much more time consuming than without the dict
# because you can have many objects with the same k (key in the index)
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

    # getting the inner indexes for lat and lon
    lat_index = catalog.getIndex('geo_latitude')._index
    lon_index = catalog.getIndex('geo_longitude')._index

    # define decimal values
    d_tlat_min = Decimal(str(tlat_min))
    d_tlat_max = Decimal(str(tlat_max))

    d_tlon_min = Decimal(str(tlon_min))
    d_tlon_max = Decimal(str(tlon_max))

    # adjust to cover results outside frame, but very close to margins
    # trying to fix cluster flickering near margins

    # applying the lat and lon indexes to get the rids
    rs = None
    lat_set, lat_dict = _apply_index_with_range_dict_results(lat_index, d_tlat_min, d_tlat_max)
    rs = intersection(rs, lat_set)

    lon_set, lon_dict = _apply_index_with_range_dict_results(lon_index, d_tlon_min, d_tlon_max)
    rs = intersection(rs, lon_set)

    rs_final = []
    # OR the filters and apply the index for each one

    for f in filters:
        rs_f = rs

        #adjust geo limits in filters to be consistent with discretized tile limits
        f['geo_longitude']['query'] = (d_tlon_min, d_tlon_max)
        f['geo_latitude']['query'] = (d_tlat_min, d_tlat_max)

        #this code is from the search function in the catalog implementation in Zope
        for idx_name in f:
            index = catalog.getIndex(idx_name)
            r = index._apply_index(f)
            if r is not None:
                r, _ = r
                rs_f = intersection(rs_f, r)

        rs_final.append(rs_f)

    r_list = list(multiunion(rs_final))

    # transform objects to points
    points = []
    for i in range(len(r_list)):
        points.append(clusters.Point(i, float(lat_dict[r_list[i]]), float(lon_dict[r_list[i]])))

    centers, groups = clusters.kmeans(tlat_min, tlat_max, tlon_min, tlon_max, points, grid_size)

    # transform group points to rids
    for i in range(len(groups)):
        groups[i] = map(lambda p: r_list[p.id], groups[i])

    return centers, groups
