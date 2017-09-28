"""
This module contains the class that handles check-in/check-out operations for a
single object.
"""


from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from constants import *

class NyCheckControl:
    """Class that implements functionality for check-in/check-out operations.
    It is an `abstract class` in the sense that a set of functions are not
    implemented.

    """

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Initialize variables.

        checkout
            integer value (0 or 1) that stores the state of the object
            (locked/unlocked).

        checkout_user
            string value that stores the id of the user that locked the object.

        version
            stores all the modified object data during the locking operation.
        """
        self.checkout = 0
        self.checkout_user = None
        self.version = None

    def getVersionProperty(self, id):
        """Returns a non multilingual object property value.

        If the object has been locked then the value is retrieved from the
        version otherwise from the object directly

        """

        if self.checkout:
            return getattr(self.version, id)
        else:
            return getattr(self, id)

    def getVersionLocalProperty(self, id, lang):
        """ Returns a multilingual object property value.

        Arguments::

            id -- the name of the object property
            lang -- the language code

        Returns::

            - if the object has been locked then the value is retrieved
              from the version
            - if the object it is not locked then the value is retrieved
              from the object

        """

        if self.checkout:
            return self.version.getLocalProperty(id, lang)
        else:
            return self.getLocalProperty(id, lang)

    def isVersionAuthor(self):
        """Checks if the current authenticated user is the one that locked the
        object.

        """

        return self.checkout_user == self.REQUEST.AUTHENTICATED_USER.getUserName()

    def hasVersion(self):
        """ Checks if the object is locked."""

        return (self.checkout == 1) and (self.version is not None)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """Handles the commit operation.

        `This method must be implemented`

        """

        raise EXCEPTION_NOTIMPLEMENTED, 'commitVersion'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """Handles the locking operation.

        `This method must be implemented`

        """

        raise EXCEPTION_NOTIMPLEMENTED, 'startVersion'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'discardVersion')
    def discardVersion(self, REQUEST=None):
        """ Handles the discard operation. """

        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

InitializeClass(NyCheckControl)
