"""Drop map records under containers the current user cannot View."""

import time
import uuid

from AccessControl import getSecurityManager
from AccessControl.Permissions import view
from Acquisition import aq_base
from BTrees.IIBTree import IISet, difference

CACHE_TTL = 60
# containers scanned even when they hold no geo-tagged objects yet
CONTAINER_META_TYPES = ('Naaya Folder', 'Naaya Photo Folder',
                        'Naaya Photo Gallery', 'Naaya Forum Topic')

# site path -> (serial, scan time, sorted paths of restricted containers)
_restricted_cache = {}


def invalidate(context):
    """Call after changing the View permission of a container."""
    portal_map = getattr(context.getSite(), 'portal_map', None)
    if portal_map is not None:
        # random, so an aborted change never repeats a cached value
        portal_map._view_restrictions_serial = uuid.uuid4().hex


def _site_path(site):
    return '/'.join(site.getPhysicalPath())


def scan_restricted_containers(site, catalog):
    """Paths of containers whose View permission is not acquired."""
    site_path = _site_path(site)
    candidates = set()
    rids = list(catalog.getIndex('geo_latitude')._unindex.keys())
    meta_type_index = catalog.getIndex('meta_type')._index
    container_rids = set()
    for meta_type in CONTAINER_META_TYPES:
        found = meta_type_index.get(meta_type)
        if found is None:
            continue
        container_rids.update([found] if isinstance(found, int) else found)
    for rid in container_rids:
        candidates.add(catalog.getpath(rid))
    for rid in rids:
        path = catalog.getpath(rid)
        while True:
            path = path.rsplit('/', 1)[0]
            if len(path) <= len(site_path) or path in candidates:
                break
            candidates.add(path)
    restricted = []
    for path in candidates:
        if not path.startswith(site_path + '/'):
            continue
        ob = site.unrestrictedTraverse(path[len(site_path) + 1:], None)
        if ob is None:
            continue
        if isinstance(getattr(aq_base(ob), '_View_Permission', None), tuple):
            restricted.append(path)
    return sorted(restricted)


def restricted_containers(portal_map, catalog):
    site = portal_map.getSite()
    key = _site_path(site)
    serial = getattr(portal_map, '_view_restrictions_serial', None)
    cached = _restricted_cache.get(key)
    now = time.time()
    if cached is not None and cached[0] == serial and \
            now - cached[1] < CACHE_TTL:
        return cached[2]
    paths = scan_restricted_containers(site, catalog)
    _restricted_cache[key] = (serial, now, paths)
    return paths


def denied_rids(portal_map, catalog):
    """IISet of catalog rids the current user cannot View, or None."""
    user = getSecurityManager().getUser()
    request = getattr(portal_map, 'REQUEST', None)
    other = getattr(request, 'other', None)
    cache_key = ('_naaya_geo_denied_rids', id(user), user.getId(),
                 getattr(portal_map, '_view_restrictions_serial', None))
    if other is not None and cache_key in other:
        return other[cache_key]

    site = portal_map.getSite()
    site_path = _site_path(site)
    check = getSecurityManager().checkPermission
    denied = []
    # sorted paths list parents before children
    for path in restricted_containers(portal_map, catalog):
        if denied and path.startswith(denied[-1] + '/'):
            continue
        ob = site.unrestrictedTraverse(path[len(site_path) + 1:], None)
        if ob is not None and not check(view, ob):
            denied.append(path)
    result = None
    if denied:
        result = catalog.getIndex('path')._apply_index(
            {'path': {'query': denied, 'level': 0}})[0]
    if other is not None:
        other[cache_key] = result
    return result


def filter_rids(portal_map, catalog, rids):
    """Remove denied rids; keeps the order of a list."""
    denied = denied_rids(portal_map, catalog)
    if not denied:
        return rids
    if isinstance(rids, list):
        denied = set(denied)  # faster membership than IISet
        return [rid for rid in rids if rid not in denied]
    return difference(IISet(rids), denied)


def can_view(ob):
    return bool(getSecurityManager().checkPermission(view, ob))
