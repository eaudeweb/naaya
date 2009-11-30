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
from os.path import join

#Zope imports
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from NyForumBase import NyForumBase
from Products.NaayaCore.managers.utils import utils
from NyForumTopic import manage_addNyForumTopic_html, topic_add_html, addNyForumTopic
from Products.NaayaBase.NyGadflyContainer import manage_addNyGadflyContainer
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES

STATISTICS_CONTAINER = '.statistics'
STATISTICS_COLUMNS = {'topic': 'VARCHAR', 'hits': 'INTEGER'}

manage_addNyForum_html = PageTemplateFile('zpt/forum_manage_add', globals())
def manage_addNyForum(self, id='', title='', description='', categories='', file_max_size=0, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYFORUM + self.utGenRandomId(6)
    categories = self.utConvertLinesToList(categories)
    file_max_size = abs(int(file_max_size))
    ob = NyForum(id, title, description, categories, file_max_size)
    self._setObject(id, ob)
    self._getOb(id).loadDefaultData()
    if not REQUEST:
        return id
    # Redirect
    if not REQUEST.form.get('redirect_url', None):
        return self.manage_main(self, REQUEST, update_menu=1)
    REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

class NyForum(NyForumBase, Folder, utils):
    """ """

    meta_type = METATYPE_NYFORUM
    meta_label = LABEL_NYFORUM
    icon = 'misc_/NaayaForum/NyForum.gif'
    icon_marked = 'misc_/NaayaForum/NyForum_marked.gif'

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

    _Add_Naaya_Forum_Message_Permission = ['Anonymous']
    _Add_Edit_Delete_Naaya_Forum_Topic_Permission = ['Administrator', 'Manager']
    _Naaya___Skip_Captcha_Permission = ['Administrator', 'Manager']

    #constructors
    security.declareProtected(view_management_screens, 'manage_addNyForumTopic_html')
    manage_addNyForumTopic_html = manage_addNyForumTopic_html

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'topic_add_html')
    topic_add_html = topic_add_html

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'addNyForumTopic')
    addNyForumTopic = addNyForumTopic

    def __init__(self, id, title, description, categories, file_max_size):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.categories = categories
        self.file_max_size = file_max_size
        NyForumBase.__dict__['__init__'](self)
        #make this object available for portal search engine
        self.submitted = 1
        self.approved = 1

    def __setstate__(self,state):
        """
        For backwards compatibility.
        """
        NyForum.inheritedAttribute("__setstate__") (self, state)
        if not hasattr(self, 'file_max_size'):
            self.file_max_size = 0

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """
        Load data:
            - specific email template
        """
        #load specific email template
        emailtool_ob = self.getEmailTool()
        if emailtool_ob._getOb(EMAILTEMPLATE_NOTIFICATIONONREPLY_ID, None) is None:
            content = self.futRead(join(NAAYAFORUM_PRODUCT_PATH, 'data', '%s.txt' % EMAILTEMPLATE_NOTIFICATIONONREPLY_ID), 'r')
            emailtool_ob.manage_addEmailTemplate(EMAILTEMPLATE_NOTIFICATIONONREPLY_ID, EMAILTEMPLATE_NOTIFICATIONONREPLY_TITLE, content)

    #api
    def get_forum_object(self): return self
    def get_forum_path(self, p=0): return self.absolute_url(p)
    def get_forum_categories(self): return self.categories
    def get_topics(self): return self.objectValues(METATYPE_NYFORUMTOPIC)
    def count_topics(self): return len(self.objectIds(METATYPE_NYFORUMTOPIC))

    def getObjectsForValidation(self): return []
    def count_notok_objects(self): return 0
    def count_notchecked_objects(self): return 0

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
                    if file.filename.find('\\') != -1:
                        id = file.filename.split('\\')[-1]
                    else:
                        id = file.filename
                    #check file size
                    id = self.utCleanupId(id)
                    if len(file.read()) <= self.file_max_size or self.file_max_size == 0:
                        ob.manage_addFile(id=id, file=file)

    def can_be_seen(self):
        """
        Indicates if the current user has access to the current forum.
        """
        return self.checkPermission(view)

    def has_restrictions(self):
        """
        Indicates if this folder has restrictions for the current user.
        """
        return not self.acquiredRolesAreUsedBy(view)

    def get_roles_with_access(self):
        """
        Returns a list of roles that have access to this forum.
        """
        r = []
        ra = r.append
        for x in self.rolesOfPermission(view):
            if x['selected'] and x['name'] not in ['Administrator', 'Anonymous', 'Manager', 'Owner']:
                ra(x['name'])
        return r

    security.declareProtected(view, 'getPublishedFolders')
    def getPublishedFolders(self):
        return self.objectValues(METATYPE_NYFORUMTOPIC)

    def getPublishedObjects(self): return []
    def getObjects(self): return self.getPublishedFolders()
    def getPendingFolders(self): return []
    def getFolders(self): return self.getPublishedFolders()
    def hasContent(self): return (len(self.getObjects()) > 0)

    security.declarePrivate('notifyOnMessage')
    def notifyOnMessage(self, msg):
        """
        When a new message is created, checks all its parents
        for B{notify} flag. If on, then send email notification.
        """
        #process the list of emails
        authenticationtool_ob = self.getAuthenticationTool()
        d = {}
        for x in msg.get_message_parents(msg):
            if x.notify:
                ob = authenticationtool_ob.getUser(x.author)
                if ob: d[ob.email] = 0
        #send emails
        emailtool_ob = self.getEmailTool()
        email_template = emailtool_ob._getOb(EMAILTEMPLATE_NOTIFICATIONONREPLY_ID)
        l_from = self.getSite().mail_address_from
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@URL@@', '%s#%s' % (msg.get_topic_path(), msg.id))
        for e in d.keys():
            emailtool_ob.sendEmail(l_content, e, l_from, l_subject)

    security.declareProtected(view, 'checkTopicsPermissions')
    def checkTopicsPermissions(self):
        """
        This function is called on the forum index and it checkes whether or not
        to display the various buttons on that form.
        Returns in a list of tuples: which buttons should be visible,
        a list of topics, sorted reversed by the date of the last post.
        """
        import operator
        r = []
        ra = r.append
        btn_select, btn_delete, can_operate = 0, 0, 0
        # btn_select - if there is at least one permisson to delete or copy an object
        # btn_delete - if there is at least one permisson to delete an object
        for x in self.objectValues(METATYPE_NYFORUMTOPIC):
            del_permission = x.checkPermissionModifyForumTopic()
            edit_permission = x.checkPermissionModifyForumTopic()
            if del_permission: btn_select = 1
            if del_permission: btn_delete = 1
            if edit_permission: can_operate = 1
            ra((del_permission, edit_permission, x, x.get_last_message().postdate))
        can_operate = can_operate or btn_select
        return btn_select, btn_delete, can_operate, sorted(r, key=operator.itemgetter(3), reverse=True)

    def checkPermissionSkipCaptcha(self):
        return getSecurityManager().checkPermission('Naaya - Skip Captcha', self)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', categories='', file_max_size='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self.categories = self.utConvertLinesToList(categories)
        self.file_max_size = abs(int(file_max_size))
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #zmi actions
    security.declareProtected(PERMISSION_ADD_FORUM, 'saveProperties')
    def saveProperties(self, title='', description='', categories='', file_max_size='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self.categories = self.utConvertLinesToList(categories)
        self.file_max_size = abs(int(file_max_size))
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'deleteTopics')
    def deleteTopics(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Topic(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())
    
    #
    # Statistics
    #
    security.declarePrivate("_getStatisticsContainer")
    def _getStatisticsContainer(self):
        """ Create statistics container if it doesn't exists and return it
        """
        scontainer = getattr(self, STATISTICS_CONTAINER, None)
        if not scontainer:
            return manage_addNyGadflyContainer(self, STATISTICS_CONTAINER, 
                                               **STATISTICS_COLUMNS)
        return scontainer
    
    security.declareProtected(view, 'getTopicHits')
    def getTopicHits(self, topic):
        """ Returns statistics for given topic
        """
        scontainer = self._getStatisticsContainer()
        res = scontainer.get('HITS', topic=topic)
        if not res:
            return 0
        return res[0]['HITS']
    
    security.declareProtected(view, 'updateTopicHits')
    def updateTopicHits(self, topic):
        """ Update hits for topic
        """
        scontainer = self._getStatisticsContainer()
        res = scontainer.get('HITS', topic=topic)
        if not res:
            return scontainer.add(hits=1, topic=topic)
        hits = res[0]['HITS']
        hits += 1
        return scontainer.set(key='hits', value=hits, topic=topic)
    
    security.declareProtected(view, 'hasVersion')
    def hasVersion(self):
        """ """
        return False

    security.declarePublic('export_this')
    def export_this(self, folderish=0):
        """ """
        return ''

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/forum_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/forum_index', globals())
    
    security.declareProtected(PERMISSION_ADD_FORUM, 'edit_html')
    edit_html = PageTemplateFile('zpt/forum_edit', globals())
    
    security.declareProtected(PERMISSION_ADD_FORUM, 'forum_add_html')
    forum_add_html = PageTemplateFile('zpt/forum_add', globals())
    
InitializeClass(NyForum)
