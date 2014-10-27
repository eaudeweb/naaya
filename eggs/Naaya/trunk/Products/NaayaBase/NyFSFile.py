"""
This module contains the class that implements the Naaya file system
file type of object. All types of objects that are file system files
must extend this class.
"""

from zope.interface import implements
from Globals import InitializeClass
from OFS.Image import File, Pdata   #, getImageInfo
from interfaces import INyFSFile
# from Products.ExtFile.ExtFile import ExtFile
# from Products.ExtFile.ExtImage import ExtImage
from naaya.content.bfile.NyBlobFile import NyBlobFile

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
        self._bfile = NyBlobFile(id=id, title=title, size=0)

    def __setstate__(self, state):
        """ Updates """

        NyFSFile.inheritedAttribute("__setstate__") (self, state)
        if not hasattr(self, '_bfile'):
            etitle = getattr(self, 'title', 'File system data')
            eid = getattr(self, '__name__', 'data.fs')
            self._bfile = NyBlobFile(id=eid, title=etitle, size=0)

    def _update_properties(self, **properties):
        for property, value in properties.items():
            ext_property = getattr(self._bfile, property, None)
            if ext_property is None:
                raise KeyError('Unknown property %s' % property)
            setattr(self._bfile, property, value)
        self._p_changed = 1

    def _update_data(self, data, content_type='', filename=''):
        self.manage_beforeUpdate()
        if hasattr(data, '__class__') and data.__class__ is Pdata:
            data = str(data)
        if not data:
            return
        if filename:
            self._bfile.id = filename
        self.data = ''
        if isinstance(data, NyBlobFile):
            self._bfile = data
            self.size = self._bfile.get_size()
            return
        return self._bfile.write_data(data, content_type)

    def _get_data_name(self):
        data = self.get_data(as_string=False)
        return getattr(data, 'filename', [])

    def get_data(self, as_string=True):
        if as_string:
            if hasattr(self, '_ext_file'):  #not migrated yet?
                if self._bfile.size == 0:
                    return self._ext_file.index_html()
            return self._bfile.index_html()

        if hasattr(self, '_ext_file'):  #not migrated yet?
            if self._bfile.size == 0:
                return self._ext_file.index_html()
        return self._bfile

    #
    # Adapt File methods to ExtFile.
    #
    def manage_beforeUpdate(self, item=None, container=None):
        self_id = getattr(self, '__name__', 'data.fs')
        self._bfile = NyBlobFile(id=self_id, title=self.title_or_id())

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

        self._bfile.PUT(REQUEST, RESPONSE)

    def manage_FTPget(self):
        """ Handle FTP GET requests"""

        return self._bfile.manage_FTPget()

InitializeClass(NyFSFile)

