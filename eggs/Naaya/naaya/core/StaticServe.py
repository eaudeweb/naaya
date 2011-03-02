import os
from Globals import package_home
from zipfile import ZipFile

from zope2util import CaptureTraverse
from utils import mimetype_from_filename

class StaticServeFromZip(object):
    """ Serves static files from the filesystem """

    def __init__(self, path, zipfile, _globals=None):
        if _globals:
            import os
            zipfile = os.path.join(package_home(_globals), zipfile)

        self._path = path
        self._zipfile = zipfile

    def __bobo_traverse__(self, REQUEST, name):
        return StaticServeFromZip(self._path + '/' + name, self._zipfile)

    def __call__(self, REQUEST):
        """ serve a static file """
        # print "the path is [%s]; the zipfile is [%s]" % (self._path, self._zipfile)
        zf = ZipFile(self._zipfile)

        try:
            data = zf.read(self._path)
            content_type = mimetype_from_filename(self._path)
            if content_type:
                REQUEST.RESPONSE.setHeader('content-type', content_type)
                REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=31556926')
        except KeyError:
            data = "Not Found"
            REQUEST.RESPONSE.setStatus(404)

        zf.close()
        return data

def StaticServeFromFolder(path, _globals=None, cache=True):
    """ Serves static files from the filesystem """

    if _globals:
        _path = os.path.join(package_home(_globals), path)
    else:
        _path = path

    def callback(context, path, REQUEST):
        filepath = os.path.join(_path, *path)
        try:
            fd = open(filepath, 'rb')
        except IOError:
            REQUEST.RESPONSE.setStatus(404)
            return "Not Found"

        try:
            data = fd.read()
            content_type = mimetype_from_filename(filepath)
            if content_type:
                REQUEST.RESPONSE.setHeader('content-type', content_type)
                if cache:
                    REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=31556926')
                else:
                    REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
        except KeyError:
            data = "Not Found"
            REQUEST.RESPONSE.setStatus(404)

        fd.close()
        return data

    return CaptureTraverse(callback)
