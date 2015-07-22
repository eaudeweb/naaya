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
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

"""
This module contains the class that implements functionality for uploading and
inserting images using the Epoz WYSIWYG editor. This is used to edit object
properties that contains HTML code.
"""

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from AccessControl.Permissions import view
from OFS.Image import manage_addImage, manage_addFile

#Product imports
from Products.NaayaCore.managers.utils import utils

class NyEpozToolbox:
    """
    Class that implements functionality for uploading and inserting images
    using the Epoz WYSIWYG editor.
    """

    security = ClassSecurityInfo()

    #api
    def getUploadedImages(self):
        """
        Returns a list with all I{Image} objects.
        """
        return self.objectValues(['Image'])

    #actions
    security.declareProtected(view, 'process_image_upload')
    def process_image_upload(self, file='', REQUEST=None):
        """
        Handles the upload of a new image.
        @param file: uploaded image
        @param REQUEST: I{optional} parameter to do the redirect
        """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    pos = max(file.filename.rfind('/'), file.filename.rfind('\\'), file.filename.rfind(':'))+1
                    id = file.filename[pos:]
                    ph = file.filename[:pos]
                    while True:
                        try:
                            manage_addImage(self, '', file)
                            break
                        except:
                            rand_id = utils().utGenRandomId(6)
                            file.filename = '%s%s_%s' % (ph, rand_id , id)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    security.declareProtected(view, 'process_file_upload')
    def process_file_upload(self, file='', REQUEST=None):
        """
        Handles the upload of a new file.
        @param file: uploaded file
        @param REQUEST: I{optional} parameter to do the redirect
        """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    manage_addFile(self, '', file)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    security.declareProtected(view, 'process_delete')
    def process_delete(self, ids=[], REQUEST=None):
        """
        Handles the deletion of one or more images and files.
        @param ids: the ids of the objects
        @type ids: list
        @param REQUEST: I{optional} parameter to do the redirect
        """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: pass
        if REQUEST: REQUEST.RESPONSE.redirect('%s/toolbox_html' % self.absolute_url())

    #pages
    security.declareProtected(view, 'toolbox_html')
    def toolbox_html(self, REQUEST=None, RESPONSE=None):
        """
        The page template that is the interface between the WYSIWYG editor
        and the uploaded images and files.
        """
        return self.getFormsTool().getContent({'here': self}, 'epoz_toolbox')

InitializeClass(NyEpozToolbox)
