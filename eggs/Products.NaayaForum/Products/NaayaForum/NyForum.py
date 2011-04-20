from os.path import join

from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view, change_permissions
from zope import interface

import naaya.sql
from constants import *
from NyForumBase import NyForumBase
from Products.NaayaCore.managers.utils import utils, make_id
from NyForumTopic import (manage_addNyForumTopic_html, topic_add_html,
                          addNyForumTopic)
from feeds import messages_feed
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaBase.NyRoleManager import NyRoleManager
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaBase.NyAccess import NyAccess
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile

from interfaces import INyForum

STATISTICS_CONTAINER = '.statistics'
STATISTICS_COLUMNS = {'topic': 'VARCHAR(80) UNIQUE',
                      'hits': 'INTEGER DEFAULT 0'}

email_templates = {
    'notification-on-reply': EmailPageTemplateFile('emailpt/notification.zpt', globals()),
}

manage_addNyForum_html = PageTemplateFile('zpt/forum_manage_add', globals())
def addNyForum(self, id='', title='', description='', categories='', file_max_size=0, REQUEST=None):
    """ """
    id = make_id(self, id=id, title=title, prefix=PREFIX_NYFORUM)
    categories = self.utConvertLinesToList(categories)
    file_max_size = abs(int(file_max_size))
    ob = NyForum(id, title, description, categories, file_max_size)
    self._setObject(id, ob)
    if not REQUEST:
        return id
    # Redirect
    if not REQUEST.form.get('redirect_url', None):
        return self.manage_main(self, REQUEST, update_menu=1)
    REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

class NyForum(NyRoleManager, NyPermissions, NyForumBase, Folder, utils):
    """ """
    interface.implements(INyForum)

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

    edit_access = NyAccess('edit_access', {
        view: "Access content",
        PERMISSION_MODIFY_FORUMTOPIC: "Modify topic",
        PERMISSION_ADD_FORUMMESSAGE: "Add message",
        PERMISSION_MODIFY_FORUMMESSAGE: "Modify message",
    })

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

    security.declarePrivate('_get_template')
    def _get_template(self, name):
        template = self._getOb('emailpt_%s' % name, None)
        if template is not None:
            return template.render_email

        template = email_templates.get(name, None)
        if template is not None:
            return template.render_email

        raise ValueError('template for %r not found' % name)

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
                    id = self.utSlugify(id)
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

    security.declarePublic('getPublishedFolders')
    def getPublishedFolders(self):
        if not self.checkPermissionView():
            return []
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
        portal = self.getSite()
        authenticationtool_ob = portal.getAuthenticationTool()
        emails = set()
        for m in msg.get_message_parents(msg):
            if m.notify:
                user = authenticationtool_ob.get_user_with_userid(m.author)
                if user: emails.add(authenticationtool_ob.getUserEmail(user))

        #build message body
        msg_body = {
            'url': '%s#%s' % (msg.get_topic_path(), msg.id),
            'site_title': self.site_title,
            'title': msg.title_or_id(),
            'description': self.html2text(msg.description, trim_length=None),
            'author': msg.author,
            'postdate': self.utShowFullDateTime(msg.postdate),
                   }

        template = self._get_template('notification-on-reply')
        mail_data = template(**msg_body)

        #send emails
        email_tool = portal.getEmailTool()
        for email in emails:
            email_tool.sendEmail(p_content = mail_data['body_text'],
                                 p_to = email,
                                 p_from = email_tool._get_from_address(),
                                 p_subject = mail_data['subject'])

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'deleteTopics')
    def deleteTopics(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrorsTrans('Error while delete data.')
        else: self.setSessionInfoTrans('Topic(s) deleted.')
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #
    # Statistics
    #
    security.declarePrivate("_getStatisticsContainer")
    def _getStatisticsContainer(self):
        """ Create statistics container if it doesn't exists and return it
        """
        stats_container = getattr(self, STATISTICS_CONTAINER, None)
        if stats_container is None:
            stats_container = naaya.sql.new_db()
            setattr(self, STATISTICS_CONTAINER, stats_container)
            table = ("CREATE TABLE HITS"
                     "(id INTEGER PRIMARY KEY ASC AUTOINCREMENT")
            for (col, val) in STATISTICS_COLUMNS.items():
                table += ", " + col + " " + val
            table += ")"
            stats_container.cursor().execute(table)
        return stats_container

    def _removeStatisticsContainer(self):
        """ Remove statistics container if exists
        """
        stats_container = getattr(self, STATISTICS_CONTAINER, None)
        if stats_container is not None:
            if hasattr(stats_container, 'drop'):
                stats_container.drop()
            delattr(self, STATISTICS_CONTAINER)

    security.declareProtected(view, 'getTopicHits')
    def getTopicHits(self, topic):
        """ Returns statistics for given topic
        """
        cursor = self._getStatisticsContainer().cursor()
        cursor.execute("SELECT hits from HITS where topic=?", (topic,))
        res = cursor.fetchone()
        if not res:
            cursor.execute("INSERT into HITS(topic) values(?)", (topic,))
            return 0
        else:
            return res[0]

    security.declarePrivate('setTopicHits')
    def setTopicHits(self, topic, how_many=1):
        hits = self.getTopicHits(topic) + how_many
        stats_container = self._getStatisticsContainer()
        stats_container.cursor().execute("UPDATE HITS set hits=? where topic=?",
                                    (hits, topic))

    security.declareProtected(view, 'updateTopicHits')
    def updateTopicHits(self, topic):
        """ Update hits for topic
        """
        self.setTopicHits(topic, 1)

    security.declareProtected(view, 'removeTopicHits')
    def removeTopicHits(self, topic):
        """ Remove hits record for topic
        """
        stats_container = self._getStatisticsContainer()
        stats_container.cursor().execute("DELETE FROM HITS where topic=?",
                                         (topic, ))

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

    security.declareProtected(view, 'messages_feed')
    messages_feed = messages_feed

    security.declareProtected(PERMISSION_ADD_FORUM, 'edit_html')
    edit_html = PageTemplateFile('zpt/forum_edit', globals())

    security.declareProtected(PERMISSION_ADD_FORUM, 'forum_add_html')
    forum_add_html = PageTemplateFile('zpt/forum_add', globals())

InitializeClass(NyForum)
