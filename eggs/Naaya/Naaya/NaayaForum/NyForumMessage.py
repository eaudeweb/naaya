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
import Products
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *

manage_addNyForumMessage_html = PageTemplateFile('zpt/message_manage_add', globals())
message_add_html = PageTemplateFile('zpt/message_add', globals())
def addNyForumMessage(self, id='', title='', description='', attachment='',
    REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYFORUMMESSAGE + self.utGenRandomId(6)
    author, postdate = self.processIdentity()
    if self.meta_type == METATYPE_NYFORUMTOPIC: uid = None
    else: uid = self.utGenerateUID()
    ob = NyForumMessage(id, title, description, author, postdate, uid)
    self._setObject(id, ob)
    self.handleAttachmentUpload(self._getOb(id), attachment)
    if REQUEST is not None:
        referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if referer == 'manage_addNyForumMessage_html' or \
            referer.find('manage_addNyForumMessage_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif referer == 'message_add_html':
            REQUEST.RESPONSE.redirect(self.absolute_url())

class NyForumMessage(Folder):
    """ """

    meta_type = METATYPE_NYFORUMMESSAGE
    icon = 'misc_/NaayaForum/NyForumMessage.gif'

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['File']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, author, postdate, uid):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.author = author
        self.postdate = postdate
        self._uid = uid

    #api
    def get_message_object(self): return self
    def get_message_path(self, p=0): return self.absolute_url(p)
    def get_message_uid(self): return self._uid
    def get_attachments(self): return self.objectValues('File')

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/message_manage_edit', globals())

InitializeClass(NyForumMessage)
