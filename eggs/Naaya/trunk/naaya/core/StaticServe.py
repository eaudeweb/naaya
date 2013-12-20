"""This is a convenient method to serve static resources using Zope.
Used for serving javascript libraries, stylesheets and others.
The usage is quite simple. Say you have a :term:`OFS` class named
`MyNewProduct` and you have a few javascripts a stylesheets located in a `www`
directory where you class is::

    class MyNewProduct(SimpleItem):

        www = StaticServeFromFolder('path_to_my_folder', globals())

Now if you have an object instance say /folder/MyNewProduct all your resources
will be accessible like this::

    http://....//folder/MyNewProduct/www/some_javascript.js
    http://....//folder/MyNewProduct/www/deeper/css.js
    ...

..note:: The use of this method to server static content is discouraged.
The zope server shouldn't server static content directly. Until another method
"""
import os
import mimetypes
from Globals import package_home
from zipfile import ZipFile

from zope2util import CaptureTraverse


class StaticServeFromZip(object):
    """ Serves static files from a zip file"""

    def __init__(self, path, zipfile, _globals=None):
        if _globals:
            import os
            zipfile = os.path.join(package_home(_globals), zipfile)

        self._path = path
        self._zipfile = zipfile

    def __bobo_traverse__(self, REQUEST, name):
        """ """
        return StaticServeFromZip(self._path + '/' + name, self._zipfile)

    def __call__(self, REQUEST):
        """ serve a static file """
        # print "the path is [%s]; the zipfile is [%s]" % (self._path, self._zipfile)
        zf = ZipFile(self._zipfile)

        try:
            data = zf.read(self._path)
            content_type, content_encoding = mimetypes.guess_type(self._path)
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
            content_type, content_encoding = mimetypes.guess_type(filepath)
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
