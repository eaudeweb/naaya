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

manage_addNyForumMessage_html = PageTemplateFile('zpt/message_manage_add', globals())
message_add_html = PageTemplateFile('zpt/message_add', globals())
def addNyForumMessage(self, id='', inreplyto='', title='', description='', attachment='',
    notify='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYFORUMMESSAGE + self.utGenRandomId(6)
    if inreplyto == '': inreplyto = None
    if notify: notify = 1
    else: notify = 0
    author, postdate = self.processIdentity()
    uid = self.utGenerateUID()
    ob = NyForumMessage(id, inreplyto, title, description, notify, author, postdate, uid)
    self._setObject(id, ob)
    ob = self._getOb(id)
    self.handleAttachmentUpload(ob, attachment)
    self.notifyOnMessage(ob)
    if REQUEST is not None:
        referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if referer == 'manage_addNyForumMessage_html' or \
            referer.find('manage_addNyForumMessage_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif referer == 'message_add_html':
            REQUEST.RESPONSE.redirect(self.absolute_url())

class NyForumMessage(Folder, NyForumBase):
    """ """

    meta_type = METATYPE_NYFORUMMESSAGE
    meta_label = LABEL_NYFORUMMESSAGE
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

    def __init__(self, id, inreplyto, title, description, notify, author,
        postdate, uid):
        """ """
        self.id = id
        self._inreplyto = inreplyto
        self.title = title
        self.description = description
        self.notify = notify
        self.author = author
        self.postdate = postdate
        self._uid = uid
        NyForumBase.__dict__['__init__'](self)

    #api
    def get_message_object(self): return self
    def get_message_path(self, p=0): return self.absolute_url(p)
    def get_message_inreplyto(self): return self._inreplyto
    def set_message_inreplyto(self, v):
        self._inreplyto = v
        self._p_changed = 1
    def get_message_uid(self): return self._uid
    def get_attachments(self): return self.objectValues('File')

    #site actions
    security.declareProtected(PERMISSION_MODIFY_FORUMMESSAGE, 'saveProperties')
    def saveProperties(self, title='', description='', notify='', REQUEST=None):
        """ """
        if notify: notify = 1
        else: notify = 0
        self.title = title
        self.description = description
        self.notify = notify
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMMESSAGE, 'deleteAttachments')
    def deleteAttachments(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Attachment(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMMESSAGE, 'addAttachment')
    def addAttachment(self, attachment='', REQUEST=None):
        """ """
        self.handleAttachmentUpload(self, attachment)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_ADD_FORUMMESSAGE, 'replyMessage')
    def replyMessage(self, title='', description='', attachment='', notify='',
        REQUEST=None):
        """ """
        id = PREFIX_NYFORUMMESSAGE + self.utGenRandomId(6)
        addNyForumMessage(self.get_topic_object(), id, self.get_message_uid(),
            title, description, attachment, notify)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s#%s' % (self.get_topic_path(), id))

    security.declareProtected(PERMISSION_MODIFY_FORUMMESSAGE, 'deleteMessage')
    def deleteMessage(self, nodes='', REQUEST=None):
        """ """
        topic = self.get_topic_object()
        parent_msg = self.get_message_parent(self)
        child_msgs = self.get_message_childs(self)
        if nodes:
            #remove all child nodes
            topic.manage_delObjects([x.id for x in child_msgs])
        else:
            #move child nodes (replies to this message)
            if parent_msg is None: new_puid = None
            else: new_puid = parent_msg.get_message_uid()
            for msg in child_msgs:
                msg.set_message_inreplyto(new_puid)
        #remove message itself
        topic.manage_delObjects([self.id])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect(topic.absolute_url())

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', notify='', REQUEST=None):
        """ """
        if notify: notify = 1
        else: notify = 0
        self.title = title
        self.description = description
        self.notify = notify
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/message_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/message_index', globals())

    security.declareProtected(PERMISSION_MODIFY_FORUMMESSAGE, 'edit_html')
    edit_html = PageTemplateFile('zpt/message_edit', globals())

    security.declareProtected(PERMISSION_MODIFY_FORUMMESSAGE, 'delete_html')
    delete_html = PageTemplateFile('zpt/message_delete', globals())

    security.declareProtected(PERMISSION_ADD_FORUMMESSAGE, 'reply_html')
    reply_html = PageTemplateFile('zpt/message_reply', globals())

InitializeClass(NyForumMessage)
