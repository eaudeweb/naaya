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
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from AccessControl.Permissions import view
from OFS.Image import manage_addImage, manage_addFile

#Product imports

class NyEpozToolbox:
    """ """

    def __init__(self):
        """ """
        pass

    security = ClassSecurityInfo()

    #api
    def getUploadedImages(self): return self.objectValues(['Image'])

    #actions
    security.declareProtected(view, 'process_image_upload')
    def process_image_upload(self, file='', REQUEST=None):
        """ """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    manage_addImage(self, '', file)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    security.declareProtected(view, 'process_file_upload')
    def process_file_upload(self, file='', REQUEST=None):
        """ """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    manage_addFile(self, '', file)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    security.declareProtected(view, 'process_delete')
    def process_delete(self, ids=[], REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: pass
        if REQUEST: REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    #pages
    security.declareProtected(view, 'toolbox_html')
    def toolbox_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'epoz_toolbox')

InitializeClass(NyEpozToolbox)
