from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from zope import interface

import naaya.sql
from constants import *
from NyForumBase import NyForumBase
from Products.NaayaCore.managers.utils import utils, make_id
from NyForumTopic import (manage_addNyForumTopic_html, topic_add_html,
                          addNyForumTopic)
from feeds import messages_feed
from Products.NaayaBase.constants import (MESSAGE_SAVEDCHANGES,
                                          PERMISSION_SKIP_CAPTCHA)
from Products.NaayaBase.NyRoleManager import NyRoleManager
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaBase.NyAccess import NyAccess
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.i18n.LocalPropertyManager import LocalProperty, LocalPropertyManager

from interfaces import INyForum

STATISTICS_CONTAINER = '.statistics'
STATISTICS_COLUMNS = {'topic': 'VARCHAR(80) UNIQUE',
                      'hits': 'INTEGER DEFAULT 0'}

manage_addNyForum_html = PageTemplateFile('zpt/forum_manage_add', globals())
def addNyForum(self, id='', title='', description='', categories='', file_max_size=0, REQUEST=None):
    """ """
    id = make_id(self, id=id, title=title, prefix=PREFIX_NYFORUM)
    categories = self.utConvertLinesToList(categories)
    file_max_size = abs(int(file_max_size))
    contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    ob = NyForum(id, title, description, categories, file_max_size, contributor)
    ob.releasedate = self.process_releasedate()
    self._setObject(id, ob)
    self[id].loadDefaultData()
    if not REQUEST:
        return id
    # Redirect
    if not REQUEST.form.get('redirect_url', None):
        return self.manage_main(self, REQUEST, update_menu=1)
    REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

class NyForum(NyRoleManager, NyPermissions, NyForumBase, Folder, utils,
                LocalPropertyManager):
    """ """
    interface.implements(INyForum)

    meta_type = METATYPE_NYFORUM
    meta_label = LABEL_NYFORUM
    icon = 'misc_/NaayaForum/NyForum.gif'
    icon_marked = 'misc_/NaayaForum/NyForum_marked.gif'
    topics_listing = 'Plain table'
    topics_ordering = 'Reverse: Chronological order'
    message_top = LocalProperty('message_top')
    message_outdated = LocalProperty('message_outdated')

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

    def __init__(self, id, title, description, categories, file_max_size, contributor):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.categories = categories
        self.file_max_size = file_max_size
        self.contributor = contributor
        NyForumBase.__dict__['__init__'](self)
        #make this object available for portal search engine
        self.submitted = 1
        self.approved = 1

    def loadDefaultData(self):
        """
        Sets default permissions
        """
        self.manage_permission(PERMISSION_ADD_FORUMMESSAGE,
                               ['Anonymous'], acquire=1)
        self.manage_permission(PERMISSION_MODIFY_FORUMTOPIC,
                               ['Administrator', 'Manager'], acquire=1)
        self.manage_permission(PERMISSION_SKIP_CAPTCHA,
                               ['Administrator', 'Manager'], acquire=1)

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

    def get_sort_options(self):
        """ return a maping of sorting options"""
        return [['Subject', 'subject', False],
                ['Access type', 'access', False],
                ['Status', 'status', False],
                ['Author', 'author', False],
                ['Number of replies', 'count_messages', False],
                ['Number of views', 'views', False],
                ['Chronological order', 'last_message', False],
                ['Reverse: Subject', 'subject', True],
                ['Reverse: Access type', 'access', True],
                ['Reverse: Status', 'status', True],
                ['Reverse: Author', 'author', True],
                ['Reverse: Number of replies', 'count_messages', True],
                ['Reverse: Number of views', 'views', True],
                ['Reverse: Chronological order', 'last_message', True]]

    security.declareProtected(view, 'checkTopicsPermissions')
    def checkTopicsPermissions(self):
        """
        This function is called on the forum index and it checkes whether or not
        to display the various buttons on that form.
        Returns in a list of tuples: which buttons should be visible,
        a list of topics, sorted reversed by the date of the last post.
        """
        REQUEST = self.REQUEST
        skey = REQUEST.get('skey', None)
        rkey = None
        if skey is None:
            for option in self.get_sort_options():
                if self.topics_ordering == option[0]:
                    skey = option[1]
                    rkey = option[2]
        if rkey is None:
            rkey = REQUEST.get('rkey')
            if not rkey:
                rkey = False
            else:
                rkey = rkey not in ['0', 'False']
        if self.topics_listing == 'Plain table':
            topics = {'Plain table': []}
        else:
            topics = {}
            for category in self.categories:
                topics[category] = []
        btn_select, btn_delete, can_operate = 0, 0, 0
        # btn_select - if there is at least one permisson to delete or copy an object
        # btn_delete - if there is at least one permisson to delete an object
        for x in self.objectValues(METATYPE_NYFORUMTOPIC):
            del_permission = x.checkPermissionModifyForumTopic()
            edit_permission = x.checkPermissionModifyForumTopic()
            if del_permission: btn_select = 1
            if del_permission: btn_delete = 1
            if edit_permission: can_operate = 1
            if self.topics_listing == 'Plain table':
                topics['Plain table'].append((del_permission, edit_permission, x))
            else:
                if x.category in topics.keys():
                    topics[x.category].append((del_permission, edit_permission, x))
                elif 'Other' in topics.keys():
                    topics['Other'].append((del_permission, edit_permission, x))
                else:
                    topics['Other'] = [(del_permission, edit_permission, x)]
        can_operate = can_operate or btn_select
        for topics_category in topics.values():
            if skey == 'subject':
                topics_category.sort(key=lambda x: x[2].title_or_id().lower(),
                        reverse=rkey)
            elif skey == 'access':
                topics_category.sort(key=lambda x: x[2].access_type(),
                        reverse=rkey)
            elif skey == 'status':
                topics_category.sort(key=lambda x: x[2].is_topic_opened(),
                        reverse=rkey)
            elif skey == 'views':
                topics_category.sort(key=lambda x:
                        self.getTopicHits(topic=x[2].id), reverse=rkey)
            elif skey == 'last_message':
                topics_category.sort(key=lambda x:
                        x[2].get_last_message().postdate, reverse=rkey)
            else:
                try:
                    topics_category.sort(key=lambda x: getattr(x[2], skey),
                        reverse=rkey)
                except AttributeError:
                    #This means the sort key was wrong (manually altered)
                    pass
        return btn_select, btn_delete, can_operate, topics, skey, rkey

    def checkPermissionSkipCaptcha(self):
        return getSecurityManager().checkPermission('Naaya - Skip Captcha', self)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', categories='', file_max_size='', topics_listing='', topics_ordering='', REQUEST=None):
        """ """
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.contributor = contributor
        self.title = title
        self.description = description
        self.categories = self.utConvertLinesToList(categories)
        self.file_max_size = abs(int(file_max_size))
        self.topics_listing = topics_listing
        self.topics_ordering = topics_ordering
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #zmi actions
    security.declareProtected(PERMISSION_ADD_FORUM, 'saveProperties')
    def saveProperties(self, title='', description='', categories='',
        file_max_size='', topics_listing='', topics_ordering='',
        message_top='', message_outdated='', alphabetic_categories=None,
        REQUEST=None):
        """ """
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.contributor = contributor
        self.title = title
        self.description = description
        self.categories = self.utConvertLinesToList(categories)
        self.file_max_size = abs(int(file_max_size))
        self.topics_listing = topics_listing
        self.topics_ordering = topics_ordering
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('message_top', lang, message_top)
        self._setLocalPropValue('message_outdated', lang, message_outdated)
        self.alphabetic_categories = alphabetic_categories
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'deleteTopics')
    def deleteTopics(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrorsTrans('Error while deleting data.')
        else: self.setSessionInfoTrans('Topic(s) deleted.')
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #
    # Statistics
    #
    security.declarePrivate("_getStatisticsContainerCursor")
    def _getStatisticsContainerCursor(self):
        """ Create statistics container if it doesn't exists and return it
        """
        stats_container = getattr(self, STATISTICS_CONTAINER, None)
        if stats_container is None:
            # do DB was ever created
            cursor = None
        else:
            try:
                cursor = stats_container.cursor()
            except naaya.sql.DbMissing:
                # DB was removed
                cursor = None

        if cursor is None:
            stats_container = naaya.sql.new_db()
            setattr(self, STATISTICS_CONTAINER, stats_container)
            table = ("CREATE TABLE HITS"
                     "(id INTEGER PRIMARY KEY ASC AUTOINCREMENT")
            for (col, val) in STATISTICS_COLUMNS.items():
                table += ", " + col + " " + val
            table += ")"
            cursor = stats_container.cursor()
            cursor.execute(table)

        return cursor

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
        cursor = self._getStatisticsContainerCursor()
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
        cursor = self._getStatisticsContainerCursor()
        cursor.execute("UPDATE HITS set hits=? where topic=?", (hits, topic))

    security.declareProtected(view, 'updateTopicHits')
    def updateTopicHits(self, topic):
        """ Update hits for topic
        """
        self.setTopicHits(topic, 1)

    security.declareProtected(view, 'removeTopicHits')
    def removeTopicHits(self, topic):
        """ Remove hits record for topic
        """
        cursor = self._getStatisticsContainerCursor()
        cursor.execute("DELETE FROM HITS where topic=?", (topic, ))

    security.declareProtected(view, 'hasVersion')
    def hasVersion(self):
        """ """
        return False

    security.declarePublic('export_this')
    def export_this(self, folderish=0):
        """ """
        return ''

    security.declareProtected(view, 'get_categories')
    def get_categories(self):
        """ return categories, sorted if the option is set on the forum
        """
        if getattr(self, 'alphabetic_categories', None):
            return sorted(self.categories)
        return self.categories

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/forum_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/forum_index', globals(), 'forum_index')

    security.declareProtected(view, 'messages_feed')
    messages_feed = messages_feed

    security.declareProtected(PERMISSION_ADD_FORUM, 'edit_html')
    edit_html = PageTemplateFile('zpt/forum_edit', globals())

    security.declareProtected(PERMISSION_ADD_FORUM, 'forum_add_html')
    forum_add_html = PageTemplateFile('zpt/forum_add', globals())

InitializeClass(NyForum)
