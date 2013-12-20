from decimal import Decimal

from BTrees.IIBTree import IISet, union, weightedIntersection, weightedUnion

from Products.NaayaCore.GeoMapTool import clusters

# this is much more time consuming than without the dict
# because you can have many objects with the same k (key in the index)
def _apply_index_with_range_dict_results(index, low_value=None, high_value=None):
    """ return an IISet of the rids matching the range in the index
        also return a dict matching each rid to the value of the index for that rid
    """
    index_items = index.items(low_value, high_value)

    r_set = None
    r_dict = dict()
    for k, kset in index_items:
        if isinstance(kset, int):
            r_dict[kset] = k
            kset = IISet((kset,))
        else:
            for kitem in kset:
                r_dict[kitem] = k
        r_set = union(r_set, kset)
    if isinstance(r_set, int):
        r_set = IISet((r_set, ))
    if r_set is None:
        r_set = IISet()
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

    # adjust to cover results outside frame, but very close to margins
    # trying to fix cluster flickering near margins

    # applying the lat and lon indexes to get the rids
    rs = None
    lat_set, lat_dict = _apply_index_with_range_dict_results(lat_index, Decimal(str(tlat_min)), Decimal(str(tlat_max)))
    w, rs = weightedIntersection(rs, lat_set)

    lon_set, lon_dict = _apply_index_with_range_dict_results(lon_index, Decimal(str(tlon_min)), Decimal(str(tlon_max)))
    w, rs = weightedIntersection(rs, lon_set)

    rs_final = None
    # OR the filters and apply the index for each one
    for f in filters:
        rs_f = rs

        #adjust geo limits in filters to be consistent with discretized tile limits
        f['geo_longitude']['query'] = (Decimal(str(tlon_min)), Decimal(str(tlon_max)))
        f['geo_latitude']['query'] = (Decimal(str(tlat_min)), Decimal(str(tlat_max)))

        #this code is from the search function in the catalog implementation in Zope
        for i in catalog.indexes.keys():
            index = catalog.getIndex(i)
            _apply_index = getattr(index, "_apply_index", None)
            if _apply_index is None:
                continue
            r = _apply_index(f)

            if r is not None:
                r, u = r
                w, rs_f = weightedIntersection(rs_f, r)

        w, rs_final = weightedUnion(rs_f, rs_final)

    r_list = list(rs_final)

    # transform objects to points
    points = []
    for i in range(len(r_list)):
        points.append(clusters.Point(i, float(lat_dict[r_list[i]]), float(lon_dict[r_list[i]])))

    centers, groups = clusters.kmeans(tlat_min, tlat_max, tlon_min, tlon_max, points, grid_size)

    # transform group points to rids
    for i in range(len(groups)):
        groups[i] = map(lambda p: r_list[p.id], groups[i])

    return centers, groups

