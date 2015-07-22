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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#   Alin Voinea, Eau de Web
""" 
This module contains the class that implements the Naaya file system 
folder type of object. All types of objects that are file system containers 
must extend this class.
"""
import zLOG
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.NaayaBase.NyContainer import NyContainer

EXTFILE_INSTALLED = True
try:
    from Products.ExtFile.ExtFile import manage_addExtFile
except ImportError:
    zLOG.LOG("NyFSContainer", zLOG.WARNING, 
             "ExtFile is not installed => all files will be stored in ZODB")
    EXTFILE_INSTALLED = False

class NyFSContainer(NyContainer):
    """ Class that implements the Naaya file system folder type of object.
    """
    is_ext = EXTFILE_INSTALLED
    def __init__(self):
        NyContainer.__init__(self)
    
    def manage_addFile(self, id, file="", **kwargs):
        if self.is_ext:
            return manage_addExtFile(self, id=id, file=file)
        return NyContainer.manage_addFile(self, id, file)
    
    def isReady(self, fid):
        """ Check if file exists
        """
        doc = self._getOb(fid)
        if not self.is_ext:
            return doc and True or False
        return not doc.is_broken()

InitializeClass(NyFSContainer)
