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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyComments import NyComments
from Products.NaayaCore.managers.utils import utils

class blog_comment_item(utils):
    """
    Class that implements a blog comment.
    """

    def __init__(self, id, title, body, author, email, date, entry):
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
        self.email = email
        self.date = date
        self.entry = entry

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    security.declarePublic('export_this')
    def export_this(self):
        """
        Exports object into Naaya XML format.
        """
        return '<comment id="%s" title="%s" body="%s" author="%s" email="%s" date="%s"/>' % \
            (self.utXmlEncode(self.id),
                self.utXmlEncode(self.title),
                self.utXmlEncode(self.body),
                self.utXmlEncode(self.author),
                self.utXmlEncode(self.email),
                self.utXmlEncode(self.date))

InitializeClass(blog_comment_item)

class NyBlogComments(NyComments):
    """ """

    security = ClassSecurityInfo()

    def __init__(self):
        """ Constructor. """
        NyComments.__dict__['__init__'](self)

    security.declarePrivate('add_comment_item')
    def add_comment_item(self, id, title, body, author, email, date, entry):
        """
        Create a new blog comment.
        """
        item = blog_comment_item(id, title, body, author, email, date, entry)
        self.insert_comment_obj(id, item)

    security.declarePrivate('import_comments')
    def import_comments(self, discussion):
        """
        Import blog comments.
        """
        if discussion is not None:
            for comment in discussion.comments:
                self.comment_add(comment.id, comment.title, comment.body,
                    comment.author.encode('utf-8'), comment.email.encode('utf-8'), comment.date.encode('utf-8'), comment.entry.encode('utf-8'))

    #site actions
    security.declareProtected(view, 'comment_add')
    def comment_add(self, id='', title='', body='', author=None, email='', date=None, contact_word='', REQUEST=None):
        """
        Add a blog comment for this object.
        """
        username = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if username != 'Anonymous User':
            a_tool = self.getAuthenticationTool()
            user = a_tool.getUser(username)
            author = a_tool.getUserFullName(user)
            email = a_tool.getUserEmail(user)

        err = []
        id = self.utCleanupId(id)
        if not id: id = self.utGenRandomId()
        if author is None:
            author = self.REQUEST.AUTHENTICATED_USER.getUserName()
            email = ''
        if date is None: date = self.utGetTodayDate()
        else: date = self.utGetDate(date)
        if author.strip() == '' or email.strip() == '':
            err.append('Please fill the required fields (name, email)')
        if username == 'Anonymous User':
            if contact_word=='' or contact_word!=self.getSession('captcha', None):
                err.append('The word you typed does not match with the one shown in the image. Please try again.')
            self.delSession('captcha')
        if len(err) > 0:
            if REQUEST:
                self.setBlogSession(title, body, author, email)
                self.setSessionErrorsTrans(err)
                REQUEST.RESPONSE.redirect('%s/blogcomment_add_html' % self.absolute_url())
        else:
            self.delBlogSession()
            self.add_comment_item(id, title, body, author, email, date, self.absolute_url(1))
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #site pages
    security.declareProtected(view, 'blogcomments_box')
    def blogcomments_box(self, REQUEST=None, RESPONSE=None):
        """
        List all the blog comments for this object.
        """
        return self.getFormsTool().getContent({'here': self}, 'blogcomments_box')

    security.declareProtected(view, 'blogcomment_add_html')
    def blogcomment_add_html(self, REQUEST=None, RESPONSE=None):
        """
        Form for adding a new blog comment.
        """
        return self.getFormsTool().getContent({'here': self}, 'blogcomment_add')

InitializeClass(NyBlogComments)
