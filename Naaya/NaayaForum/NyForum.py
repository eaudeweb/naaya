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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaCore.managers.utils import utils
from NyForumTopic import manage_addNyForumTopic_html, topic_add_html, addNyForumTopic

manage_addNyForum_html = PageTemplateFile('zpt/forum_manage_add', globals())
def manage_addNyForum(self, id='', title='', description='', categories='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYFORUM + self.utGenRandomId(6)
    categories = self.utConvertLinesToList(categories)
    ob = NyForum(id, title, description, categories)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NyForum(Folder, utils):
    """ """

    meta_type = METATYPE_NYFORUM
    icon = 'misc_/NaayaForum/NyForum.gif'

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_NYFORUMTOPIC, 'action': 'manage_addNyForumTopic_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    #constructors
    security.declareProtected(view_management_screens, 'manage_addNyForumTopic_html')
    manage_addNyForumTopic_html = manage_addNyForumTopic_html

    security.declareProtected(PERMISSION_MANAGE_FORUMTOPIC, 'topic_add_html')
    topic_add_html = topic_add_html

    security.declareProtected(PERMISSION_MANAGE_FORUMTOPIC, 'addNyForumTopic')
    addNyForumTopic = addNyForumTopic

    def __init__(self, id, title, description, categories):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.categories = categories

    #api
    def get_forum_object(self): return self
    def get_forum_path(self, p=0): return self.absolute_url(p)
    def get_forum_categories(self): return self.categories
    def get_topics(self): return self.objectValues(METATYPE_NYFORUMTOPIC)
    def count_topics(self): return len(self.objectIds(METATYPE_NYFORUMTOPIC))

    security.declarePrivate('processIdentity')
    def processIdentity(self):
        """
        Returns information about the user who created the topic/message
        and the posting date.
        """
        return self.REQUEST.AUTHENTICATED_USER.getUserName(), self.utGetTodayDate()

    security.declarePrivate('handleAttachmentUpload')
    def handleAttachmentUpload(self, ob, file):
        """
        Handle upload of a file. A B{File} object will be created inside
        the B{given} object.
        """
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    ob.manage_addFile(id='', file=file)

    #permissions
    def checkPermissionManageForumTopic(self):
        return getSecurityManager().checkPermission(PERMISSION_MANAGE_FORUMTOPIC, self) is not None

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', categories='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self.categories = self.utConvertLinesToList(categories)
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_MANAGE_FORUMTOPIC, 'deleteObjects')
    def deleteObjects(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Topic(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/forum_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/forum_index', globals())

InitializeClass(NyForum)
