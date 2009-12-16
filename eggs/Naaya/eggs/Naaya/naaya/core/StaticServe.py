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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

from Globals import package_home
from zipfile import ZipFile


content_types = {
    '.html' : 'text/html',
    '.htm'  : 'text/html',
    '.xml'  : 'text/xml',
    '.css'  : 'text/css',
    '.js'   : 'application/x-javascript',
    '.gif'  : 'image/gif',
    '.jpg'  : 'image/jpeg',
    '.jpeg' : 'image/jpeg',
    '.png'  : 'image/png',
    '.swf'  : 'application/x-shockwave-flash',
}

def get_content_type(path):
    if not path.rfind('.') > path.rfind('/'):
        return None
    
    ext = path[path.rfind('.'):]
    return content_types.get(ext, None)

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
            content_type = get_content_type(self._path)
            if content_type:
                REQUEST.RESPONSE.setHeader('content-type', content_type)
                REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=31556926')
        except KeyError:
            data = "Not Found"
            REQUEST.RESPONSE.setStatus(404)
        
        zf.close()
        return data
