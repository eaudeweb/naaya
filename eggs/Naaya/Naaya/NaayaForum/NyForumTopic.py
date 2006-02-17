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
from NyForumBase import NyForumBase
from Products.NaayaBase.constants import *
from NyForumMessage import manage_addNyForumMessage_html, message_add_html, addNyForumMessage

manage_addNyForumTopic_html = PageTemplateFile('zpt/topic_manage_add', globals())
topic_add_html = PageTemplateFile('zpt/topic_add', globals())
def addNyForumTopic(self, id='', title='', category='', description='',
    attachment='', notify='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYFORUMTOPIC + self.utGenRandomId(6)
    if notify: notify = 1
    else: notify = 0
    author, postdate = self.processIdentity()
    ob = NyForumTopic(id, title, category, description, notify, author, postdate)
    self._setObject(id, ob)
    self.handleAttachmentUpload(self._getOb(id), attachment)
    if REQUEST is not None:
        referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if referer == 'manage_addNyForumTopic_html' or \
            referer.find('manage_addNyForumTopic_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif referer == 'topic_add_html':
            REQUEST.RESPONSE.redirect(self.absolute_url())

class NyForumTopic(Folder, NyForumBase):
    """ """

    meta_type = METATYPE_NYFORUMTOPIC
    meta_label = LABEL_NYFORUMTOPIC
    icon = 'misc_/NaayaForum/NyForumTopic.gif'

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
        {'name': METATYPE_NYFORUMMESSAGE, 'action': 'manage_addNyForumMessage_html'},
    )
    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['File']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        y.extend(self.meta_types)
        return y

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_addNyForumMessage_html')
    manage_addNyForumMessage_html = manage_addNyForumMessage_html

    security.declareProtected(PERMISSION_ADD_FORUMMESSAGE, 'message_add_html')
    message_add_html = message_add_html

    security.declareProtected(PERMISSION_ADD_FORUMMESSAGE, 'addNyForumMessage')
    addNyForumMessage = addNyForumMessage

    def __init__(self, id, title, category, description, notify, author, postdate):
        """ """
        self.id = id
        self.title = title
        self.category = category
        self.description = description
        self.notify = notify
        self.author = author
        self.postdate = postdate
        NyForumBase.__dict__['__init__'](self)

    #api
    def get_topic_object(self): return self
    def get_topic_path(self, p=0): return self.absolute_url(p)
    def get_messages(self): return self.objectValues(METATYPE_NYFORUMMESSAGE)
    def count_messages(self): return len(self.objectIds(METATYPE_NYFORUMMESSAGE))
    def get_attachments(self): return self.objectValues('File')

    def __get_messages_thread(self, msgs, node, depth):
        """
        Recursive function that process the given messages and returns
        a tree like structure.
        """
        tree = []
        l = [msg for msg in msgs if msg.get_message_inreplyto() == node]
        map(msgs.remove, l)
        for msg in l:
            tree.append((depth, msg))
            tree.extend(self.__get_messages_thread(msgs, msg.get_message_uid(), depth+1))
        return tree

    def get_messages_thread(self):
        """
        Process all the messages and returns a structure to be displayed as
        a tree.
        """
        return self.__get_messages_thread(self.objectValues(METATYPE_NYFORUMMESSAGE), None, 1)

    def get_last_message(self):
        """
        Returns the last posted message. If the topic has no messages then
        it returns the topic itself, otherwise the last posted message.
        """
        l = self.objectValues(METATYPE_NYFORUMMESSAGE)
        if len(l)==0:
            return self
        else:
            return self.utSortObjsListByAttr(l, 'postdate', 1)[0]

    #site actions
    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'saveProperties')
    def saveProperties(self, title='', category='', description='', notify='',
        REQUEST=None):
        """ """
        if notify: notify = 1
        else: notify = 0
        self.title = title
        self.category = category
        self.description = description
        self.notify = notify
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'deleteAttachments')
    def deleteAttachments(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Attachment(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'addAttachment')
    def addAttachment(self, attachment='', REQUEST=None):
        """ """
        self.handleAttachmentUpload(self, attachment)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', category='', description='', notify='',
        REQUEST=None):
        """ """
        if notify: notify = 1
        else: notify = 0
        self.title = title
        self.category = category
        self.description = description
        self.notify = notify
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/topic_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/topic_index', globals())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'edit_html')
    edit_html = PageTemplateFile('zpt/topic_edit', globals())

InitializeClass(NyForumTopic)
