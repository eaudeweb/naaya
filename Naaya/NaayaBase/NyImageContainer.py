"""Container for storing images used in HTML documents"""
# Python imports
from urlparse import urljoin

# Zope Imports
from Products.PythonScripts.standard import url_quote
from OFS.Image import manage_addImage , cookId
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

import Acquisition

class NyImageContainer(Acquisition.Implicit):
    """Container for storing images used in HTML documents"""

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    def __init__(self, storage, relative=False, baseURL=''):
        """__init__(self, storage, relative=False,baseURL=''):
            @param storage: a folderish object where to store the images
            @param relative: the images are stored in a location
            @param baseURL: relative storage location
        """
        self.storage = storage
        self.relative = relative
        self.baseURL = baseURL

    security.declarePrivate('_redirectBack')
    def _redirectBack(self, REQUEST):
        """Go back to the referring page"""
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def uploadImage(self, file, REQUEST=None):
        """Upload image to the collection and then return to the referring URL."""
        id, title = cookId(None, None, file)
        i = 0
        while self.storage._getOb(id, None):
            i += 1
            id = '%s_%u' % (id, i)
        manage_addImage(self.storage, id, file, title)
        self._redirectBack(REQUEST)

    def deleteImages(self, ids, REQUEST=None):
        """Delete images from the collection

            @param ids: image ids
        """
        self.storage.manage_delObjects(ids)
        self._redirectBack(REQUEST)

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
