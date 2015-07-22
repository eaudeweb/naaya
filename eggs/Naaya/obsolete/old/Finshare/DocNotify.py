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
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Cornel Nitu - Finsiel Romania

#python imports
from os.path import join

#Zope imports
from Globals import InitializeClass, package_home
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.ObjectManager import BeforeDeleteException

#Product related imports
from Products.Finshare.interfaces.IDocNotify import IDocNotify
from Products.Finshare.Constants import *
from Products.Finshare.notification.Notification import Notification
from Products.Finshare.EmailTemplate import manage_addTemplate

SentinelID = 'notification'
SentinelTITLE = ''

def manage_addDocNotify(self, REQUEST=None):
    """ add notification sentinel"""
    ob = DocNotify(SentinelID, SentinelTITLE)
    self._setObject(SentinelID, ob)

    notification = open(join(package_home(globals()), 'templates','notification.txt'))
    content = notification.read()
    notification.close()
    manage_addTemplate(ob, 'newsletter', title='Notifications from FinShare', file='') #add the template in ZDOB
    obj = getattr(ob, 'newsletter')
    obj.pt_edit(text=content, content_type='')

    notification = open(join(package_home(globals()), 'templates','notification.html'))
    content = notification.read()
    notification.close()
    manage_addTemplate(ob, 'newsletter_html', title='Notifications from FinShare', file='') #add the template in ZDOB
    obj = getattr(ob, 'newsletter_html')
    obj.pt_edit(text=content, content_type='')

    sendpasswd = open(join(package_home(globals()), 'templates','forgotpassword.txt'))
    content = sendpasswd.read()
    sendpasswd.close()
    manage_addTemplate(ob, 'sendpassword', title='Your password for FinShare', file='') #add the template in ZDOB
    obj = getattr(ob, 'sendpassword')
    obj.pt_edit(text=content, content_type='')

    sendpasswd = open(join(package_home(globals()), 'templates','forgotpassword.html'))
    content = sendpasswd.read()
    sendpasswd.close()
    manage_addTemplate(ob, 'sendpassword_html', title='Your password for FinShare', file='') #add the template in ZDOB
    obj = getattr(ob, 'sendpassword_html')
    obj.pt_edit(text=content, content_type='')

    register = open(join(package_home(globals()), 'templates','registeruser.txt'))
    content = register.read()
    register.close()
    manage_addTemplate(ob, 'register', title='New user for FinShare', file='') #add the template in ZDOB
    obj = getattr(ob, 'register')
    obj.pt_edit(text=content, content_type='')

    register = open(join(package_home(globals()), 'templates','registeruser.html'))
    content = register.read()
    register.close()
    manage_addTemplate(ob, 'register_html', title='New user for FinShare', file='') #add the template in ZDOB
    obj = getattr(ob, 'register_html')
    obj.pt_edit(text=content, content_type='')

    feedback = open(join(package_home(globals()), 'templates','feedback.txt'))
    content = feedback.read()
    feedback.close()
    manage_addTemplate(ob, 'feedback', title='Feedback from Finshare', file='') #add the template in ZDOB
    obj = getattr(ob, 'feedback')
    obj.pt_edit(text=content, content_type='')

    feedback = open(join(package_home(globals()), 'templates','feedback.html'))
    content = feedback.read()
    feedback.close()
    manage_addTemplate(ob, 'feedback_html', title='Feedback from Finshare', file='') #add the template in ZDOB
    obj = getattr(ob, 'feedback_html')
    obj.pt_edit(text=content, content_type='')

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class DocNotify(Folder):
    """ send notification class """

    __implements__ = IDocNotify

    meta_type = METATYPE_DMNOTIFY
    icon = 'misc_/Finshare/folder'

    manage_options = Folder.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.members = []
        self.buffer = []

    def all_meta_types(self):
        """ """
        return ()
    
    security.declarePrivate('_filter_articles')
    def _filter_articles(self):
        """ filter all the articles from the notification list by a given property"""
        [ self.buffer.remove(x) for x in self.buffer if x.approved == 0 ]

    security.declarePrivate('_filter_members')
    def _filter_members(self):
        """ eliminate all the members without preferences """
        [ self.members.remove(x) for x in self.members if len(x.preferences) == 0 ]

    security.declarePrivate('_filter_notifications')
    def _filter_notifications(self):
        """ filter the notification list and build the output to be sent """
        ouput = []
        for user in self.members:
            buf = []
            for item in self.buffer:
                if item.thematic_area in user.preferences:
                    buf.append(item)
            output.append([user, buf])
        return output

    security.declareProtected(view, 'addMember')
    def addMember(self, username, email, firstname='', lastname='', preferences=[]):
        mb = Member(username, firstname, lastname, email, preferences)
        self.members.append(mb)
        self._filter_members()

    security.declareProtected(view, 'delMember')
    def delMember(self, username):
        [ self.members.remove(x) for x in self.members if x.username == username ]

    security.declareProtected(view, 'updateMember')
    def updateMember(self, username, email, firstname='', lastname='', preferences=[]):
        #remove old user metadata and add the new one
        [ self.members.remove(x) for x in self.members if x.username == username ]
        mb = Member(username, firstname, lastname, email, preferences)
        self.members.append(mb)
        self._filter_members()

    security.declarePrivate('addArticle')
    def addArticle(self, id, title='', thematic_area='', description='', author='', date=''):
        art = Article(id, title, thematic_area, description, author, date)
        self.buffer.append(art)

    security.declarePrivate('delArticle')
    def delArticle(self, id):
        [ self.buffer.remove(x) for x in self.buffer if x.id == id ]

    security.declareProtected('Send Finshare notifications', 'sendNotifications')
    def sendNotifications(self):
        """ """
        e = Notification()
        template = self.notification.newsletter.raw
        e.send_email('c.nitu@finsiel.ro', 'c.nitu@finsiel.ro', template)

    def manage_beforeDelete(self, item, container):
        if isinstance(item, DocNotify):
            raise BeforeDeleteException, "You cannot delete this object. It's used for notifications."

    def test(self, REQUEST=None):
        """ """
        self.addMember('cornel', 'c.nitu@finsiel.ro', 'Cornel', 'Nitu', [])

InitializeClass(DocNotify)


class Member:
    """ Member will store all the user's preferences """
    def __init__(self, username, firstname, lastname, email, preferences):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.preferences = preferences

class Article:
    """ Article will store all articles' metadata """
    def __init__(self, id, title, thematic_area, description, author, date):
        self.id = id
        self.title = title
        self.thematic_area = thematic_area
        self.description = description
        self.author = author
        self.date = date
