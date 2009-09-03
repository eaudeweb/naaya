# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

import math

import time
import random

def timecall(func):
    """ Print function's execution time. """
    def new_fn(*args, **kw):
        try:
            start = time.time()
            return func(*args, **kw)
        finally:
            duration = time.time() - start
            funcname = func.__name__
            filename = func.func_code.co_filename
            lineno = func.func_code.co_firstlineno
            print ">> %s (%s:%s):  %.3f seconds" % (funcname, filename, lineno, duration)
            new_fn.__doc__ = func.__doc__
    return new_fn


class Point:
    def __init__(self, id=-1, lat=0., lon=0.):
        self.id = id
        self.lat = lat
        self.lon = lon
    def __repr__(self):
        return '<Point id=%s lat=%s, lon=%s>' % (self.id, self.lat, self.lon)

def distance(p1, p2):
    #return ((p1.lat - p2.lat) ** 2 + (p1.lon - p2.lon) ** 2) ** 0.5
    return abs(p1.lat - p2.lat) + abs(p1.lon - p2.lon) #this one is faster


def getGridSize(zoom_level):
    """ Returns the Z of the Z*Z grid of tiles """
    return 5 * 2 ** (zoom_level - 1)

def getTileFromLatLon(zoom_level, lat, lon):
    """ Returns the x,y of the tile the lat and lon are in """
    Z = getGridSize(zoom_level)

    y = (lat + 90.) * Z / 180.
    x = (lon + 180.) * Z / 360.

    return int(math.floor(y)), int(math.floor(x))

def getLatLonFromTile(zoom_level, y, x, dy=0., dx=0.):
    """ Returns the lat and lon of the point with dx,dy inside x,y tile
    where 0. <= dx <= 1. and 0. <= dy <= 1. (selects the actual point in tile)
    """
    Z = getGridSize(zoom_level)

    lat = 180. * (y + dy) / Z - 90.
    lon = 360. * (x + dx) / Z - 180.

    return lat, lon


def get_discretized_limits(zoom_level, lat_min, lat_max, lon_min, lon_max):
    """
    Returns the tile limits that cover the map borders
    """
    # get tile limits
    ty_min, tx_min = getTileFromLatLon(zoom_level, lat_min, lon_min)
    ty_max, tx_max = getTileFromLatLon(zoom_level, lat_max, lon_max)

    # get lat, lon for the margins
    tlat_min, tlon_min = getLatLonFromTile(zoom_level, ty_min, tx_min, 0., 0.)
    tlat_max, tlon_max = getLatLonFromTile(zoom_level, ty_max, tx_max, 1., 1.)

    return (tlat_min, tlat_max, tlon_min, tlon_max)

def get_initial_centers(zoom_level, lat_min, lat_max, lon_min, lon_max):
    """
    Returns the inital considered centers.
    """
    # get tile limits
    ty_min, tx_min = getTileFromLatLon(zoom_level, lat_min, lon_min)
    ty_max, tx_max = getTileFromLatLon(zoom_level, lat_max, lon_max)

    result = []
    for y in range(ty_min, ty_max + 1):
        for x in range(tx_min, tx_max + 1):
            lat, lon = getLatLonFromTile(zoom_level, y, x, 0.5, 0.5)
            result.append(Point(-1, lat, lon))
    return result

def closest_center_index(centers, point):
    """The index in the centers list of the closest center to the point"""
    closest_i = 0
    min_dist = distance(point, centers[closest_i])
    for i in range(len(centers)):
        current_dist = distance(point, centers[i])
        if min_dist > current_dist:
            closest_i = i
            min_dist = current_dist
    return closest_i

def calc_new_centers(old_centers, points):
    """
    Calculates the new centers by grouping the points by the closest old center
    and calculating the mean point of every group.
    If a group has no points in it the old center is returned.
    """
    groups = []
    for c in old_centers:
        groups.append([])

    for p in points:
        c_i = closest_center_index(old_centers, p)
        groups[c_i].append(p)

    new_centers = []
    for g_i in range(len(groups)):
        g = groups[g_i]
        if len(g) == 0:
            center = old_centers[g_i]
        else:
            lat, lon = 0., 0.
            for p in g:
                lat += p.lat
                lon += p.lon
            lat = lat / len(g)
            lon = lon / len(g)
            center = Point(-1, lat, lon)
        new_centers.append(center)

    return new_centers, groups

def finished_kmeans(new_centers, old_centers, zoom_level):
    """
    Checks if all the distances between the new center and the old center
    of every group are smaller than a chosen value (EPSILON)
    """
    EPSILON = 20. / 2 ** zoom_level
    assert len(new_centers) == len(old_centers)

    for i in range(len(new_centers)):
        if distance(new_centers[i], old_centers[i]) > EPSILON:
            return False
    return True

def kmeans(zoom_level, lat_min, lat_max, lon_min, lon_max, points):
    """
    The centers and the groups of some points
    for a specified zoom level and map bounds
    """
    if points == []:
        return [], []

    old_centers = get_initial_centers(zoom_level, lat_min, lat_max, lon_min, lon_max)

    while True:
        new_centers, groups = calc_new_centers(old_centers, points)

        if finished_kmeans(new_centers, old_centers, zoom_level):
            break

        #remove centers with empty groups
        old_centers = []
        for i in range(len(new_centers)):
            if len(groups[i]) != 0:
                old_centers.append(new_centers[i])

    ret = ([], [])
    for i in range(len(groups)):
        if groups[i] != []:
            ret[0].append(new_centers[i])
            ret[1].append(groups[i])
    return ret

@timecall
def test_kmeans(n):
    points = []
    for i in range(n):
        #g = Point(random.uniform(-11.25, 11.25), random.uniform(-22.5, 22.5))
        g = Point(i, random.uniform(-90., 90.), random.uniform(-180., 180.))
        points.append(g)
    #kmeans(3, -11.25, 11.25, -22.5, 22.5, points)
    kmeans(0, -90., 90., -180., 180., points)

if __name__=='__main__':
    test_kmeans(5000)

