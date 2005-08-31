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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from NyBase import NyBase
from NyPermissions import NyPermissions

class NyContainer(Folder, NyBase, NyPermissions):
    """ """

    manage_options = (
        Folder.manage_options
    )

    security = ClassSecurityInfo()

    def getObjectById(self, p_id):
        #returns an object inside this one
        try: return self._getOb(p_id)
        except: return None

    def getObjectByUrl(self, p_url):
        #returns an object inside this one
        try: return self.unrestrictedTraverse(p_url, None)
        except: return None

    def getObjectsByIds(self, p_ids):
        #returns a list of objects inside this one
        return filter(lambda x: x is not None, map(lambda f, x: f(x, None), (self._getOb,)*len(p_ids), p_ids))

    def getObjectsByUrls(self, p_urls):
        #returns a list of objects inside this one
        return filter(lambda x: x is not None, map(lambda f, x: f(x, None), (self.unrestrictedTraverse,)*len(p_urls), p_urls))

    def manage_afterAdd(self, item, container):
        """ This method is called, whenever _setObject in ObjectManager gets called. """
        Folder.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

InitializeClass(NyContainer)
