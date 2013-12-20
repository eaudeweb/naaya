"""
This module contains the class that implements the Naaya file system
file type of object. All types of objects that are file system files
must extend this class.
"""

from zope.interface import implements
from Globals import InitializeClass
from OFS.Image import File, Pdata, getImageInfo
from interfaces import INyFSFile
from Products.ExtFile.ExtFile import ExtFile
from Products.ExtFile.ExtImage import ExtImage

class NyFSFile(File):
    """
    ExtFile adapter for File objects.
    """

    implements(INyFSFile)

    content_type = 'application/octet-stream' # catch-all content type

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
        NyFSImage.inheritedAttribute('update_data')(self, data, content_type,
                                     size, filename)

InitializeClass(NyFSImage)
