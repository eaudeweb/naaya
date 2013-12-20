"""
This module contains an implementation for NyCheckControl, to be used by content
types that don't support check-in/check-out.
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from constants import *

class NyNonCheckControl:
    """
    Class that implements the interface for check-in/check-out operations.
    It should be used by objects that don't support check-in/check-out.
    """

    security = ClassSecurityInfo()

    def getVersionProperty(self, id):
        return getattr(self, id)

    def getVersionLocalProperty(self, id, lang):
        return self.getLocalProperty(id, lang)

    def isVersionAuthor(self):
        raise NotImplementedError

    def hasVersion(self):
        return False

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        raise NotImplementedError

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        raise NotImplementedError

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'discardVersion')
    def discardVersion(self, REQUEST=None):
        raise NotImplementedError

InitializeClass(NyNonCheckControl)
