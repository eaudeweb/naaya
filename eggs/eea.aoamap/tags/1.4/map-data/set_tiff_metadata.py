""" Map data
"""
from __future__ import division

from osgeo import osr
from osgeo import gdal

def main():
    """ Main
    """
    import sys
    filename = sys.argv[1]

    dataset = gdal.Open(filename, gdal.GA_Update)

    a0 = 6378137
    ax = 8000000
    af = ax / a0

    ETRS_LAEA = osr.SpatialReference()
    ETRS_LAEA.ImportFromProj4("+proj=laea +lat_0=52 +lon_0=65 "
                              "+a=%d +b=%d" % (a0, a0))
    dataset.SetProjection(ETRS_LAEA.ExportToWkt())

    x_0 = -6730000 * af
    x_1 =  5035000 * af
    y_0 = -2530000 * af
    y_1 =  5540000 * af
    p_w = (x_1 - x_0) / dataset.RasterXSize
    p_h = (y_1 - y_0) / dataset.RasterYSize
    dataset.SetGeoTransform((x_0, p_w, 0, y_1, 0, -p_h))

if __name__ == '__main__':
    main()
