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
# Copyright   European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

"""
This module contains an implementation for NyCheckControl, to be used by content
types that don't support check-in/check-out.
"""

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
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
