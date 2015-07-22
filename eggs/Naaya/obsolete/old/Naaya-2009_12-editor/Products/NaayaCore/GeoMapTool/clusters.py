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

import unittest
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


def getFullGridSize(size_y, size_x, lat_min, lat_max, lon_min, lon_max):
    """ get the size of the full map grid based on the sizes for the view """
    return (
            size_y * int(math.floor(180. / abs(lat_max - lat_min))),
            size_x * int(math.floor(360. / abs(lon_max - lon_min))),
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

def getLatLonFromTile(size_y, size_x, y, x, dy=0., dx=0.):
    """ Returns the lat and lon of the point with dx,dy inside x,y tile
    where 0. <= dx <= 1. and 0. <= dy <= 1. (selects the actual point in tile)
    """

    lat = 180. * (y + dy) / size_y - 90.
    lon = 360. * (x + dx) / size_x - 180.

    return lat, lon

def get_initial_centers(lat_min, lat_max, lon_min, lon_max,
                        size_x, size_y):
    """
    Returns the inital considered centers.
    """
    ty_min, ty_max, tx_min, tx_max = tile_limits(size_y, size_x,
                                        lat_min, lat_max, lon_min, lon_max)

    result = []
    for y in range(ty_min, ty_max):
        for x in range(tx_min, tx_max):
            lat, lon = getLatLonFromTile(size_y, size_x, y, x, 0.5, 0.5)
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


def finished_kmeans(new_centers, old_centers, centers_step):
    """
    Checks if all the distances between the new center and the old center
    of every group are smaller than a chosen value (centers_step)
    """
    assert len(new_centers) == len(old_centers)

    for i in range(len(new_centers)):
        if distance(new_centers[i], old_centers[i]) > centers_step:
            return False
    return True

def kmeans(lat_min, lat_max, lon_min, lon_max,
        points, size_x, size_y=None, centers_step=None):
    """
    size_x, size_y - are the dimensions of the initial grid of centers on full map
    centers_step - small value for determining if the centers are stable
    """
    # default arguments for size_y and centers_step
    if size_y is None:
        size_y = size_x

    size_y, size_x = getFullGridSize(size_y, size_x, lat_min, lat_max, lon_min, lon_max)

    if centers_step is None:
        centers_step = 50. / max(size_x, size_y)

    # initialize
    centers, groups = [], []
    old_centers = get_initial_centers(lat_min, lat_max, lon_min, lon_max,
                                        size_x, size_y)
    centers, groups = calc_new_centers(old_centers, points)

    while not finished_kmeans(centers, old_centers, centers_step):
        # remove centers with empty groups
        old_centers = []
        for i in range(len(centers)):
            if len(groups[i]) != 0:
                old_centers.append(centers[i])

        # next calc_centers
        centers, groups = calc_new_centers(old_centers, points)

    return centers, groups


def get_discretized_limits(lat_min, lat_max, lon_min, lon_max,
        size_x, size_y=None):
    """
    Returns the tile limits that cover the map borders
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

@timecall
def test_kmeans(n):
    points = []
    for i in range(n):
        g = Point(i, random.uniform(-90., 90.), random.uniform(-180., 180.))
        points.append(g)
    centers, groups = kmeans(-90., 90., -180., 180., points, 10)

@timecall
def test_kmeans2(n):
    points = []
    for i in range(n):
        g = Point(i, random.uniform(-11.25, 11.25), random.uniform(-22.5, 22.5))
        points.append(g)
    centers, groups = kmeans(-11.25, 11.25, -22.5, 22.5, points, 10)


class TestKmeans(unittest.TestCase):
    def test_2points(self):
        points = [Point(1, 1., 1.), Point(2, 9., 9.)]
        centers, groups = kmeans(0., 10., 0., 10., points, 2)
        assert len(centers) == 2
        assert (centers[0].lat == 1.) and (centers[0].lon == 1.)
        assert (centers[1].lat == 9.) and (centers[1].lon == 9.)

    def test_3points(self):
        points = [Point(1, 1., 1.), Point(2, 9., 9.), Point(3, 3., 3.)]
        centers, groups = kmeans(0., 10., 0., 10., points, 2)
        assert len(centers) == 2
        assert (centers[0].lat == 2.) and (centers[0].lon == 2.)
        assert (centers[1].lat == 9.) and (centers[1].lon == 9.)

class TestDiscretizedLimits(unittest.TestCase):
    def test_margin(self):
        assert (get_discretized_limits(-90., 90., -180., 180., 10)
                == get_discretized_limits(-89., 89., -179., 179., 10))

if __name__=='__main__':
    test_kmeans(5000)
    test_kmeans2(5000)

    unittest.main()

