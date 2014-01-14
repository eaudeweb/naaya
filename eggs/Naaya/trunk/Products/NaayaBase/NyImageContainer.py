"""Container for storing images used in HTML documents"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Image import manage_addImage, cookId
from OFS.ObjectManager import checkValidId
from cgi import escape
from naaya.core.zope2util import sha_hexdigest
from Products.NaayaCore.managers.utils import make_id
import urllib
import Acquisition


class NyImageContainer(Acquisition.Implicit):
    """Container for storing images used in HTML documents"""

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    def __init__(self, storage, relative=False, baseURL=''):
        """
        __init__(self, storage, relative=False,baseURL=''):
        @param storage: a folderish object where to store the images
        @param relative: the images are stored in a location
        @param baseURL: relative storage location
        """

        self.storage = storage
        self.relative = relative
        self.baseURL = baseURL

    def uploadImage(self, file, REQUEST=None):
        """
        Upload image to the collection and then return to the referring URL.
        """

        sha1_hash = sha_hexdigest(file)
        for image in self.storage.objectValues('Image'):
            if not hasattr(image, 'sha1_hash'):
                image.sha1_hash = sha_hexdigest(image)
            if sha1_hash == image.sha1_hash:
                return image

        id, title = cookId(None, None, file)
        # first, determine if this is a utf-8 text and not ascii
        try:
            id.decode('ascii')
        except UnicodeError:
            id = id.decode('utf-8')

        orig_id = id
        id = make_id(self.storage, title=title)
        id = manage_addImage(self.storage, id, file, title)
        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
        ob = self.storage._getOb(id)
        return ob

    def deleteImages(self, ids, REQUEST=None):
        """Delete images from the collection

            @param ids: image ids
        """

        self.storage.manage_delObjects(ids)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def getImageURL(self, image):
        """Return the URL (absolute or relative) of the image

            @param image: image object
        """

        if self.relative:
            return '%s/%s' % (self.storage.aq_parent.absolute_url(), image.getId())
        return '%s/%s' % (self.storage.absolute_url(), image.getId())

    def getImages(self):
        """Return the list of images"""

        return self.storage.objectValues(['Image'])

InitializeClass(NyImageContainer)
