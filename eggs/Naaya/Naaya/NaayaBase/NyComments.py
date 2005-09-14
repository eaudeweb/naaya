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

class comment_item:
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

    def open_for_comments(self):
        """
        Enable(open) comments.
        """
        self.discussion = 1
        self._p_changed = 1

    def close_for_comments(self):
        """
        Disable(close) comments.
        """
        self.discussion = 0
        self._p_changed = 1

    def add_comment_item(self, id, title, body, author, date):
        """
        Create a new comment.
        """
        item = comment_item(id, title, body, author, date)
        self.__comments_collection[id] = item
        self._p_changed = 1

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

    def delete_comment_item(self, id):
        """
        Delete 1 comment.
        """
        try: del(self.__comments_collection[id])
        except: pass
        self._p_changed = 1

    #site actions
    security.declareProtected(PERMISSION_COMMENTS_OBJECTS, 'comment_add')
    def comment_add(self, title='', body='', REQUEST=None):
        """
        Add a comment for this object.
        """
        self.add_comment_item(self.utGenRandomId(), title, body,
            self.REQUEST.AUTHENTICATED_USER.getUserName(),
            self.utGetTodayDate())
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_COMMENTS_OBJECTS, 'comment_del')
    def comment_del(self, id='', REQUEST=None):
        """
        Delete a comment.
        """
        self.delete_comment_item(id)
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

    security.declareProtected(PERMISSION_COMMENTS_OBJECTS, 'comment_add_html')
    def comment_add_html(self, REQUEST=None, RESPONSE=None):
        """
        Form for adding a new comment.
        """
        return self.getFormsTool().getContent({'here': self}, 'comment_add')

InitializeClass(NyComments)
