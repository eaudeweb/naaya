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
# Copyright   European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

"""
This module contains the class that handles comments (discussion) for the
current object.

Only the types of objects for which their class extends the I{NyComments}
can be commented.
"""

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from constants import *
from Products.NaayaCore.managers.utils import utils

class comment_item(utils):
    """
    Class that implements a comment.
    """

    def __init__(self, id, title, body, author, date):
        """
        Initialize variables:

        B{id} - unique id

        B{title} - the title of the comment (subject)

        B{body} - comment's body

        B{author} - authenticated user's name

        B{date} - posting date

        """
        self.id = id
        self.title = title
        self.body = body
        self.author = author
        self.date = date

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    security.declarePublic('export_this')
    def export_this(self):
        """
        Exports object into Naaya XML format.
        """
        return '<comment id="%s" title="%s" body="%s" author="%s" date="%s" />' % \
            (self.utXmlEncode(self.id),
                self.utXmlEncode(self.title),
                self.utXmlEncode(self.body),
                self.utXmlEncode(self.author),
                self.utXmlEncode(self.date))

    def title_or_id(self):
        """
        Returns title or id.
        """
        if not self.title:
            return self.id
        else:
            return self.title

InitializeClass(comment_item)

class NyComments:
    """
    Class that handles the validation operation for a single object.
    """

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Initialize variables:

        B{discussion} - integer value that say if the object is open
        for comments or not:
            - B{1} allow comments
            - B{0} doesn't allow comments

        B{__comments_collection} - dictionary that stores all the comments

        """
        self.discussion = 0
        self.__comments_collection = {}

    #api
    security.declarePrivate('init_comments')
    def init_comments(self):
        """
        Reset comments.
        """
        self.discussion = 0
        self.__comments_collection = {}
        self._p_changed = 1

    def is_open_for_comments(self):
        """
        Test is the object is open for comments.
        """
        return self.discussion == 1

    def get_comments_collection(self):
        """
        Get the entire comments collection.
        """
        return self.__comments_collection

    def get_comments_list(self):
        """
        Return the list of comments sorted by date.
        """
        t = [(x.date, x) for x in self.__comments_collection.values()]
        t.sort()
        return [val for (key, val) in t]

    def has_comments(self):
        """
        Returns the number of comments.
        """
        return len(self.__comments_collection.keys()) > 0

    def count_comments(self):
        """
        Returns the number of comments.
        """
        return len(self.__comments_collection.keys())

    security.declarePrivate('open_for_comments')
    def open_for_comments(self):
        """
        Enable(open) comments.
        """
        self.discussion = 1
        self._p_changed = 1

    security.declarePrivate('close_for_comments')
    def close_for_comments(self):
        """
        Disable(close) comments.
        """
        self.discussion = 0
        self._p_changed = 1

    security.declarePrivate('insert_comment_obj')
    def insert_comment_obj(self, comment_id, comment_ob):
        self.__comments_collection[comment_id] = comment_ob
        self._p_changed = 1

    security.declarePrivate('add_comment_item')
    def add_comment_item(self, id, title, body, author, date):
        """
        Create a new comment.
        """
        item = comment_item(id, title, body, author, date)
        self.__comments_collection[id] = item
        self._p_changed = 1
        return item

    security.declarePrivate('update_comment_item')
    def update_comment_item(self, id, title, body):
        """
        Modify a comment.
        """
        try:
            item = self.__comments_collection[id]
        except:
            pass
        else:
            item.title = title
            item.body = body
        self._p_changed = 1

    security.declarePrivate('delete_comment_item')
    def delete_comment_item(self, id):
        """
        Delete 1 comment.
        """
        try: del(self.__comments_collection[id])
        except: pass
        self._p_changed = 1

    security.declarePrivate('export_this_comments')
    def export_this_comments(self):
        """
        Export all the comments in XML format.
        """
        r = []
        ra = r.append
        ra('<discussion>')
        for x in self.get_comments_list():
            ra(x.export_this())
        ra('</discussion>')
        return ''.join(r)

    security.declarePrivate('import_comments')
    def import_comments(self, discussion):
        """
        Import comments.
        """
        if discussion is not None:
            for comment in discussion.comments:
                self.comment_add(comment.id, comment.title, comment.body,
                    comment.author.encode('utf-8'), comment.date.encode('utf-8'))

    #permissions
    def checkPermissionAddComments(self):
        """
        Check for adding comments.
        """
        return self.checkPermission(PERMISSION_COMMENTS_ADD)

    def checkPermissionManageComments(self):
        """
        Check for managing comments.
        """
        return self.checkPermission(PERMISSION_COMMENTS_MANAGE)

    #site actions
    security.declareProtected(PERMISSION_COMMENTS_ADD, 'comment_add')
    def comment_add(self, id='', title='', body='', author=None, date=None, REQUEST=None):
        """
        Add a comment for this object.
        """
        id = self.utCleanupId(id)
        if not id: id = self.utGenRandomId()
        if author is None: author = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if date is None: date = self.utGetTodayDate()
        else: date = self.utGetDate(date)
        ob = self.add_comment_item(id, title, body, author, date)
        self.recatalogNyObject(self)
        self.notifyFolderMaintainer(self, ob, p_template="email_notifyoncomment")
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(author)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_COMMENTS_MANAGE, 'comment_del')
    def comment_del(self, id='', REQUEST=None):
        """
        Delete a comment.
        """
        self.delete_comment_item(id)
        self.recatalogNyObject(self)
        #log date
        user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(user)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #site pages
    security.declareProtected(view, 'comments_box')
    def comments_box(self, REQUEST=None, RESPONSE=None):
        """
        List all the comments for this object.
        """
        return self.getFormsTool().getContent({'here': self}, 'comments_box')

    security.declareProtected(PERMISSION_COMMENTS_ADD, 'comment_add_html')
    def comment_add_html(self, REQUEST=None, RESPONSE=None):
        """
        Form for adding a new comment.
        """
        return self.getFormsTool().getContent({'here': self}, 'comment_add')

InitializeClass(NyComments)
