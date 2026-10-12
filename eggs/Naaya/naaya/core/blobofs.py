""" OFS Image and File that keep their data in a ZODB blob """

from AccessControl.class_init import InitializeClass
from OFS.Image import File, Image, Pdata, cookId
from ZODB.blob import Blob
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


class BlobDataMixin:
    """ Store the `data` attribute of an OFS File in a ZODB blob """

    def _get_data(self):
        blob = self.__dict__.get('_blob')
        if blob is None:
            return b''
        with blob.open('r') as f:
            return f.read()

    def _set_data(self, data):
        if isinstance(data, Pdata):
            data = bytes(data)
        self._blob = Blob(data)

    data = property(_get_data, _set_data)


class BlobImage(BlobDataMixin, Image):
    """ OFS Image with blob data; meta_type stays 'Image' """


class BlobFile(BlobDataMixin, File):
    """ OFS File with blob data; meta_type stays 'File' """


InitializeClass(BlobImage)
InitializeClass(BlobFile)


def manage_addBlobImage(container, id, file, title='', precondition='',
                        content_type=''):
    """ Like OFS.Image.manage_addImage, creating a BlobImage """
    id, title = cookId(str(id), str(title), file)
    container._setObject(id, BlobImage(id, title, b'', str(content_type),
                                       str(precondition)))
    image = container._getOb(id)
    if file:
        image.manage_upload(file)
    if content_type:
        image.content_type = content_type
    notify(ObjectCreatedEvent(image))
    return id


def to_blob(ob):
    """ Return a BlobImage/BlobFile copy of a plain OFS Image/File """
    cls = BlobImage if isinstance(ob, Image) else BlobFile
    ob._p_activate()  # a ghost has an empty __dict__
    new = cls.__new__(cls)
    state = dict(ob.__dict__)
    data = state.pop('data', b'')
    new.__dict__.update(state)
    new.data = data
    return new
