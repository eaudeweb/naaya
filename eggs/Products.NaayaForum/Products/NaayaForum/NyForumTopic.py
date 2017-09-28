from OFS.Folder import Folder
import Products
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from zope import interface

from constants import *
from NyForumBase import NyForumBase
from Products.NaayaBase.constants import *
from NyForumMessage import manage_addNyForumMessage_html, message_add_html, addNyForumMessage
from Products.NaayaBase.NyRoleManager import NyRoleManager
from interfaces import INyForumTopic
from feeds import messages_feed
from naaya.core.zope2util import path_in_site

try:
    from zope.event import notify as zope_notify
    from events import NyForumTopicAddEvent, NyForumTopicEditEvent
except ImportError:
    zope_notify = None

NyForumTopic_creation_hooks = []

manage_addNyForumTopic_html = PageTemplateFile('zpt/topic_manage_add', globals())
topic_add_html = PageTemplateFile('zpt/topic_add', globals())
def addNyForumTopic(self, id='', title='', category='', description='',
    attachment='', sort_reverse=False, REQUEST=None):
    """ """
    id = self.utSlugify(id or title or PREFIX_NYFORUMTOPIC)
    author, postdate = self.processIdentity()
    #by default a topic is opened, status = 0; when closed status = 1
    status = 0
    if attachment != '' and hasattr(attachment, 'filename') and attachment.filename != '':
        if len(attachment.read()) > self.file_max_size:
            REQUEST.set('file_max_size', self.file_max_size)
            return topic_add_html.__of__(self)(REQUEST)

    ob = NyForumTopic(id, title, category, description, author, postdate, status, sort_reverse)
    self._setObject(id, ob)
    ob = self._getOb(id)
    self.handleAttachmentUpload(ob, attachment)
    for hook in NyForumTopic_creation_hooks:
        hook(ob)
    if zope_notify is not None:
        zope_notify(NyForumTopicAddEvent(ob, author))
    if REQUEST is not None:
        referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if referer == 'manage_addNyForumTopic_html' or \
            referer.find('manage_addNyForumTopic_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif referer in ['topic_add_html', 'addNyForumTopic']:
            REQUEST.RESPONSE.redirect(self.absolute_url())

class NyForumTopic(NyRoleManager, NyForumBase, Folder):
    """ """
    interface.implements(INyForumTopic)

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
        if self.is_topic_opened():
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

    sort_reverse = False
    status = 0

    def __init__(self, id, title, category, description, author, postdate, status, sort_reverse=False):
        """ """
        self.id = id
        self.title = title
        self.category = category
        self.description = description
        self.author = author
        self.postdate = postdate
        self.status = status
        NyForumBase.__dict__['__init__'](self)
        #make this object available for portal search engine
        self.submitted = 1
        self.approved = 1
        self.releasedate = postdate
        self.sort_reverse = sort_reverse

    def __getitem__(self, key):
        """ """
        if key.startswith('msg') or key.isdigit():
            try:
                return getattr(self, key)
            except AttributeError:
                self.setSessionInfo(['This message has been deleted by the owner or by a forum administrator.'])
                return self
        raise KeyError, key

    #api
    def get_topic_object(self): return self
    def get_topic_path(self, p=0): return self.absolute_url(p)
    def get_messages(self): return self.objectValues(METATYPE_NYFORUMMESSAGE)
    def count_messages(self): return len(self.objectIds(METATYPE_NYFORUMMESSAGE))
    def get_attachments(self): return self.objectValues('File')

    def is_topic_opened(self): return self.status==0
    def is_topic_closed(self): return self.status==1

    security.declarePublic('getPublishedFolders')
    def getPublishedFolders(self):
        if not self.checkPermissionView():
            return []
        return self.objectValues(METATYPE_NYFORUMMESSAGE)

    security.declarePrivate('get_message_parent')
    def get_message_parent(self, msg):
        """
        Returns the parent of the given message.
        If the message is a reply to the topic then B{None} is returned.
        """
        try: return self._getOb(msg.inreplyto)
        except: return None

    security.declarePrivate('get_message_parents')
    def get_message_parents(self, msg):
        """
        Returns a list with the parents chain from the topic's root
        to the given message.
        """
        l, p = [], msg
        while p is not None:
            p = self.get_message_parent(p)
            if p: l.append(p)
        l.append(self)
        l.reverse()
        return l

    security.declarePrivate('get_message_childs')
    def get_message_childs(self, msg):
        """
        Returns a list with all child nodes.
        """
        return [x for x in self.objectValues(METATYPE_NYFORUMMESSAGE) if x.inreplyto == msg.id]

    def __get_messages_thread(self, msgs, node, depth):
        """
        Recursive function that process the given messages and returns
        a tree like structure.
        """
        tree = []
        l = [x for x in msgs if x.inreplyto == node]
        map(msgs.remove, l)
        for x in l:
            tree.append((depth, x))
            tree.extend(self.__get_messages_thread(msgs, x.id, depth+1))
        return tree

    security.declareProtected(view, 'get_messages_thread')
    def get_messages_thread(self):
        """
        Process all the messages and returns a structure to be displayed as
        a tree.
        """
        items = self.objectValues(METATYPE_NYFORUMMESSAGE)
        if self.sort_reverse:
            items = self.utSortObjsListByAttr(items, 'postdate')
        messages_thread = self.__get_messages_thread(items, None, 1)
        #insert the top message also at the top, if it is not already there
        for (depth, message) in messages_thread:
            if message.is_top_message and depth > 1:
                messages_thread = [(1, message)] + messages_thread
                break
        return messages_thread

    security.declarePublic('get_last_message')
    def get_last_message(self):
        """
        Returns the last posted message. If the topic has no messages then
        it returns the topic itself, otherwise the last posted message.
        """
        l = self.objectValues(METATYPE_NYFORUMMESSAGE)
        if len(l)==0: return self
        else: return self.utSortObjsListByAttr(l, 'postdate', 1)[0]

    #restrictions
    def get_valid_roles(self):
        #returns a list of roles that can be used to restrict this folder
        roles = list(self.valid_roles())
        filter(roles.remove, ['Administrator', 'Anonymous', 'Manager', 'Owner'])
        return roles

    def can_be_seen(self):
        """
        Indicates if the current user has access to the current folder.
        """
        return self.checkPermission(view)

    def has_restrictions(self):
        """
        Indicates if this folder has restrictions for the current user.
        """
        return not self.acquiredRolesAreUsedBy(view)

    def access_type(self):
        """
        Returns the access level for the current user.
        """
        if not self.can_be_seen():
            return 'Restricted'
        elif self.has_restrictions():
            return 'Limited'
        else:
            return 'Public'

    def get_roles_with_access(self):
        """
        Returns a list of roles that have access to this folder.
        """
        r = []
        ra = r.append
        for x in self.rolesOfPermission(view):
            if x['selected'] and x['name'] not in ['Administrator', 'Anonymous', 'Manager', 'Owner']:
                ra(x['name'])
        return r

    #site actions
    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'saveProperties')
    def saveProperties(self, title='', category='', status='', description='',
        postdate='', sort_reverse=False, REQUEST=None):
        """ """
        try: status = abs(int(status))
        except: status = 0
        self.title = title
        self.category = category
        self.status = status
        self.description = description
        self.sort_reverse = sort_reverse
        self._p_changed = 1
        if zope_notify is not None:
            if REQUEST is not None:
                contributor = REQUEST.AUTHENTICATED_USER.getUserName()
            else:
                contributor = None
            zope_notify(NyForumTopicEditEvent(self, contributor))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'deleteAttachments')
    def deleteAttachments(self, ids='', REQUEST=None):
        """ """
        try: self.manage_delObjects(self.utConvertToList(ids))
        except: self.setSessionErrorsTrans('Error while deleting data.')
        else: self.setSessionInfoTrans('Attachment(s) deleted.')
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'addAttachment')
    def addAttachment(self, attachment='', REQUEST=None):
        """ """
        if attachment != '' and hasattr(attachment, 'filename') and attachment.filename != '':
            if len(attachment.read()) > self.file_max_size:
                REQUEST.set('file_max_size', self.file_max_size)
                return self.edit_html.__of__(self)(REQUEST)
        self.handleAttachmentUpload(self, attachment)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'subscribe_for_notifications')
    def subscribe_for_notifications(self, REQUEST):
        """ add subscription for currently-logged-in user """
        notification_tool = self.getNotificationTool()
        location = path_in_site(self)
        notification_tool.subscribe_me(REQUEST, location, 'instant')
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'setRestrictions')
    def setRestrictions(self, access='all', roles=[], REQUEST=None):
        """
        Restrict access to current folder for given roles.
        """
        err = ''
        success = False
        if access == 'all':
            #remove restrictions
            try:
                self.manage_permission(view, roles=[], acquire=1)
            except Exception, error:
                err = error
            else:
                success = True
        else:
            #restrict for given roles
            try:
                roles = self.utConvertToList(roles)
                roles.extend(['Manager', 'Administrator'])
                self.manage_permission(view, roles=roles, acquire=0)
            except Exception, error:
                err = error
            else:
                success = True
        if REQUEST:
            if err != '': self.setSessionErrorsTrans([err])
            if success: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/restrict_html' % self.absolute_url())

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', category='', status='', description='', postdate='',
        REQUEST=None):
        """ """
        try: status = abs(int(status))
        except: status = 0
        self.title = title
        self.category = category
        self.status = status
        self.description = description
        if postdate:
            if self.utGetDate(str(postdate)):
                self.postdate = self.utGetDate(str(postdate))
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    _index_html = PageTemplateFile('zpt/topic_index', globals())
    security.declareProtected(view, 'index_html')
    def index_html(self, *args, **kwargs):
        """ """
        # Update hits
        forum = self.aq_inner.aq_parent
        forum.updateTopicHits(self.id)

        return self._index_html(*args, **kwargs)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/topic_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'edit_html')
    edit_html = PageTemplateFile('zpt/topic_edit', globals())

    security.declareProtected(view, 'messages_feed')
    messages_feed = messages_feed

    security.declareProtected(PERMISSION_MODIFY_FORUMTOPIC, 'restrict_html')
    restrict_html = PageTemplateFile('zpt/topic_restrict', globals())

InitializeClass(NyForumTopic)
