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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#   Alin Voinea, Eau de Web
"""
This module contains the class that implements the Naaya file system
file type of object. All types of objects that are file system files
must extend this class.
"""
from Globals import InitializeClass
from OFS.Image import File, Pdata, getImageInfo

from Products.ExtFile.ExtFile import ExtFile
from Products.ExtFile.ExtImage import ExtImage

class NyFSFile(File):
    """ ExtFile adapter for File objects.
    """
    def __init__(self, id, title, file, content_type='', precondition=''):
        try: id = id()
        except TypeError: pass

        self.__name__ = id
        self.title = title
        self.data = ''
        self.size = 0
        self.content_type = content_type
        self.precondition = precondition
        self._ext_file = ExtFile(id, title)

    def __setstate__(self, state):
        """ Updates """
        NyFSFile.inheritedAttribute("__setstate__") (self, state)
        if not hasattr(self, '_ext_file'):
            etitle = getattr(self, 'title', 'File system data')
            eid = getattr(self, '__name__', 'data.fs')
            self._ext_file = ExtFile(eid, etitle)

    def _update_properties(self, **properties):
        for property, value in properties.items():
            ext_property = getattr(self._ext_file, property, None)
            if ext_property is None:
                raise KeyError('Unknown property %s' % property)
            setattr(self._ext_file, property, value)
        self._p_changed = 1

    def _update_data(self, data, content_type='', filename=''):
        self.manage_beforeUpdate()
        if hasattr(data, '__class__') and data.__class__ is Pdata:
            data = str(data)
        if not data:
            return
        if filename:
            self._ext_file.id = filename
        self.data = ''
        if isinstance(data, ExtFile):
            self._ext_file = data
            self.size = self._ext_file.get_size()
            return
        return self._ext_file.manage_upload(data, content_type)

    def _get_data_name(self):
        data = self.get_data(as_string=False)
        return getattr(data, 'filename', [])

    def get_data(self, as_string=True):
        if as_string:
            return self._ext_file.index_html()
        return self._ext_file
    #
    # Adapt File methods to ExtFile.
    #
    def manage_beforeUpdate(self, item=None, container=None):
        self_id = getattr(self, '__name__', 'data.fs')
        self._ext_file = ExtFile(self_id, self.title_or_id())

    def manage_afterAdd(self, item, container):
        self._ext_file.manage_afterAdd(self._ext_file, self)
        return NyFSFile.inheritedAttribute("manage_afterAdd")(self, item, container)

    def manage_afterClone(self, item):
        self._ext_file.manage_afterClone(self._ext_file)
        return NyFSFile.inheritedAttribute("manage_afterClone")(self, item)

    def manage_beforeDelete(self, item, container):
        self._ext_file.manage_beforeDelete(self._ext_file, self)
        return NyFSFile.inheritedAttribute("manage_beforeDelete")(self, item, container)

    def __str__(self):
        return self.get_data()

    def update_data(self, data, content_type=None, size=None, filename=''):
        if content_type is not None:
            self.content_type = content_type
        if size is None:
            size = len(data)
        self.size = size
        self._update_data(data, content_type, filename)
        self.ZCacheable_invalidate()
        self.ZCacheable_set(None)
        self.http__refreshEtag()

    def index_html(self, REQUEST=None, RESPONSE=None):
        return self.get_data()

    def PrincipiaSearchSource(self):
        """ Allow file objects to be searched."""
        if self.content_type.startswith('text/'):
            return self.get_data()
        return ''

    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests"""
        self._ext_file.PUT(REQUEST, RESPONSE)

    def manage_FTPget(self):
        """ Handle FTP GET requests"""
        return self._ext_file.manage_FTPget()

InitializeClass(NyFSFile)

class NyFSImage(NyFSFile):
    """ """
    width = ''
    height = ''
    def __init__(self, id, title, file, content_type='', precondition=''):
        try: id = id()
        except TypeError: pass

        self.__name__ = id
        self.title = title
        self.data = ''
        self.size = 0
        self.width = -1
        self.height = -1
        self.content_type = content_type
        self.precondition = precondition
        self._ext_file = ExtImage(id, title)

    def tag(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, css_class=None, title=None, **args):
        return self._ext_file.tag(height=height, width=width,
                                  alt=alt, scale=scale,
                                  xscale=xscale, yscale=yscale, **args)

    def __str__(self):
        return self.tag()

    def update_data(self, data, content_type=None, size=None, filename=''):
        file = data
        data, size = self._read_data(data)
        if not filename:
            filename = getattr(file, 'filename', '')
        content_type = self._get_content_type(file, data, self.__name__,
                                              'application/octet-stream')
        ct, width, height = getImageInfo(data)
        if ct:
            content_type = ct
        if width >= 0 and height >= 0:
            self.width = width
            self.height = height
        NyFSImage.inheritedAttribute('update_data')(self, data, content_type, size, filename)

InitializeClass(NyFSImage)
