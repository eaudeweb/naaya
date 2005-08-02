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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright   European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Anton Cupcea, Finsiel Romania
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from constants import *

class NyCheckControl:

    security = ClassSecurityInfo()

    def __init__(self):
        self.checkout = 0
        self.checkout_user = None
        self.version = None

    def getVersionProperty(self, id):
        if self.checkout: return getattr(self.version, id)
        else: return getattr(self, id)
    def getVersionLocalProperty(self, id, lang):
        if self.checkout: return self.version.getLocalProperty(id, lang)
        else: return self.getLocalProperty(id, lang)

    def isVersionAuthor(self): return self.checkout_user == self.REQUEST.AUTHENTICATED_USER.getUserName()
    def hasVersion(self): return (self.checkout == 1) and (self.version is not None)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        raise EXCEPTION_NOTIMPLEMENTED, 'commitVersion'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        raise EXCEPTION_NOTIMPLEMENTED, 'startVersion'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'discardVersion')
    def discardVersion(self, REQUEST=None):
        """ """
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
