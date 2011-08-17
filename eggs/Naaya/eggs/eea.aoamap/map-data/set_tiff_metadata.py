from __future__ import division

from osgeo import osr
from osgeo import gdal

def main():
    dataset = gdal.Open('cut-raster.tiff', gdal.GA_Update)

    ETRS_LAEA = osr.SpatialReference()
    ETRS_LAEA.ImportFromProj4("+proj=laea +lat_0=52 +lon_0=65")
    dataset.SetProjection(ETRS_LAEA.ExportToWkt())

    x_0 = -5645000
    y_0 = -1931000
    x_1 = 4900500
    y_1 = 5435000
    p_w = (x_1 - x_0) / dataset.RasterXSize
    p_h = (y_1 - y_0) / dataset.RasterYSize
    dataset.SetGeoTransform((x_0, p_w, 0, y_1, 0, -p_h))

if __name__ == '__main__':
    main()
