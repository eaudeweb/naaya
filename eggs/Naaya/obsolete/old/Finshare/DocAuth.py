

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

ManageUsersPermission = 'Manage users'

#python imports
import time
import string

#zope imports
from OFS.ObjectManager import ObjectManager
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUserFolder
from AccessControl.Permissions import view_management_screens, view, manage_users
from Globals import InitializeClass, PersistentMapping
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#product imports
from Products.Finshare.authentication.DocUser import User
from Products.Finshare.utils import session
from Products.Finshare.Constants import *
from Products.Finshare.notification.Notification import Notification
from Products.Finshare.authentication.CookieCrumbler import CookieCrumbler

def manage_addAuthentication(self, REQUEST=None):
    """ """
    ob = DocAuthentication('acl_users', 'User Folder')
    self._setObject('acl_users', ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class DocAuthentication(BasicUserFolder, ObjectManager, session, CookieCrumbler):

    meta_type = 'User Folder'
    icon = 'misc_/Finshare/acl_users.gif'

    manage_options = (
        {'label' : 'Users', 'action' : 'manage_users_html'},
        {'label' : 'Permissions', 'action' : 'manage_permissions_html'},
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.data = PersistentMapping()

    ###########################
    #    PRIVATE METHODS      #
    ###########################


    security.declarePrivate('_doAddUser')
    def _doAddUser(self, name, password, roles, firstname, lastname, email, **kw):
        """Create a new user. The 'password' will be the
           original input password, unencrypted. This
           method is responsible for performing any needed encryption."""

        if password is not None and self.encrypt_passwords:
            password = self._encryptPassword(password)
        self.data[name] = User(name, password, roles, firstname, lastname, email)
        self._p_changed = 1


    security.declarePrivate('_doChangeUser')
    def _doChangeUser(self, name, password, roles, firstname, lastname, email, lastupdated, notifications, **kw):
        """Modify an existing user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""

        user=self.data[name]
        if password is not None:
            if self.encrypt_passwords and not self._isPasswordEncrypted(password):
                password = self._encryptPassword(password)
            user.__ = password
        user.roles = roles
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.lastupdated = lastupdated
        user.notifications = notifications
        self._p_changed = 1


    security.declarePrivate('_doDelUsers')
    def _doDelUsers(self, names):
        """Delete one or more users."""
        for name in names:
            del self.data[name]
        self._p_changed = 1


    security.declareProtected(PERMISSION_EDIT_USERS, 'manage_addUser')
    def manage_addUser(self, user='', pwd='', cpwd='', role='', fname='', 
        lname='', email='', REQUEST=None):
        """ """
        if REQUEST and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect(REQUEST['destination'])
        errors = []
        if not string.strip(user):
            errors.append(ERROR102)
        if not string.strip(fname):
            errors.append(ERROR100)
        if not string.strip(lname):
            errors.append(ERROR101)
        if not string.strip(email):
            errors.append(ERROR104)
        if not string.strip(pwd) or not string.strip(cpwd):
            errors.append(ERROR103)
        if self.getUser(user) or (self._emergency_user and
                                  user == self._emergency_user.getUserName()):
            errors.append(ERROR105)
        if (pwd or cpwd) and (pwd != cpwd):
            errors.append(ERROR106)
        users = self.getUserNames()
        for n in users:
            us = self.getUser(n)
            if email.strip() == us.email:
                errors.append(ERROR113)
                break
            if fname == us.firstname and lname == us.lastname:
                errors.append(ERROR114)
                break
        role = self.utConvertToList(role)
        #domains are not used for the moment
        #if domains and not self.domainSpecValidate(domains):
        #    errors.append(ERROR107)
        if len(errors):
            if REQUEST is not None: 
                #save form data to session
                self.setUserSession(user, role, fname, lname, email)
                #save error to session
                self.setSessionErrors(errors)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                return errors
        self._doAddUser(user, pwd, role, fname, lname, email)
        if REQUEST is not None and REQUEST.has_key('destination'): 
            return REQUEST.RESPONSE.redirect(REQUEST['destination'])


    security.declareProtected(PERMISSION_EDIT_USERS, 'manage_changeUser')
    def manage_changeUser(self, user='', role='', fname='', lname='', email='', lastupdated='', REQUEST=None):
        """ """
        if REQUEST and REQUEST.has_key('CancelButton'):
            return REQUEST.RESPONSE.redirect(REQUEST['destination'])
        errors = []
        if not fname:
            errors.append(ERROR100)
        if not lname:
            errors.append(ERROR101)
        if not email:
            errors.append(ERROR104)
        user_ob = self.getUser(user)
        role = self.utConvertToList(role)
        if len(errors):
            if REQUEST is not None:
                #save form data to session
                self.setUserSession(user, role, fname, lname, email)
                #save error to session
                self.setSessionErrors(errors)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                return errors
        #domains are not used for the moment
        #if domains and not self.domainSpecValidate(domains):
        #    errors.append(ERROR107)
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(user, self.getUserPassword(user_ob), role, fname, lname, email, lastupdated, [])
        if REQUEST is not None and REQUEST.has_key('destination'): 
            return REQUEST.RESPONSE.redirect(REQUEST['destination'] + '?save=ok')


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'changeUserAccount')
    def changeUserAccount(self, user='', fname='', lname='', email='', REQUEST=None, RESPONSE=None):
        """ change user account information """
        errors = []
        if not fname:
            errors.append(ERROR100)
        if not lname:
            errors.append(ERROR101)
        if not email:
            errors.append(ERROR104)
        user_ob = self.getUser(user)
        if len(errors):
            if REQUEST is not None:
                #save form data to session
                self.setUserSession(user, '', fname, lname, email)
                #save error to session
                self.setSessionErrors(errors)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                return errors
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(user, self.getUserPassword(user_ob), self.getUserRoles(user_ob), fname, lname, email, lastupdated, [])
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER + '?save=ok')


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'changeUserPassword')
    def changeUserPassword(self, user='', opass='', npass='', cpass='', REQUEST=None, RESPONSE=None):
        """ change user password """
        errors = []
        if not opass:
            errors.append(ERROR115)
        if (npass or cpass) and (npass != cpass):
            errors.append(ERROR106)
        if npass == cpass == '':
            errors.append(ERROR103)
        user_ob = self.getUser(user)
        if opass != self.getUserPassword(user_ob):
            errors.append(ERROR116)
        if len(errors):
            if REQUEST is not None:
                #save form data to session
                self.setUserSession(user, '', '', '', '')
                #save error to session
                self.setSessionErrors(errors)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                return errors
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(user, npass, self.getUserRoles(user_ob), self.getUserFirstName(user_ob), 
            self.getUserLastName(user_ob), self.getUserEmail(user_ob), lastupdated, [])
        self.credentialsChanged(user, npass)
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER + '?save=ok')


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'changeUserNotifications')
    def changeUserNotifications(self, user='', newsletter=[], REQUEST=None, RESPONSE=None):
        """ change user notifications list """
        if newsletter:
            notifications = self.utConvertToList(newsletter)
        else:
            notifications = []
        user_ob = self.getUser(user)
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(user, self.getUserPassword(user_ob), self.getUserRoles(user_ob), 
            self.getUserFirstName(user_ob), self.getUserLastName(user_ob), 
            self.getUserEmail(user_ob), lastupdated, notifications)
        if REQUEST is not None: 
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER + '?save=ok')


    security.declarePublic('registerUser')
    def registerUser(self, user='', fname='', lname='', email='', npass='', 
                    cpass='', REQUEST=None, RESPONSE=None):
        """ register a new user """
        errors = []
        if not string.strip(user):
            errors.append(ERROR102)
        if not string.strip(fname):
            errors.append(ERROR100)
        if not string.strip(lname):
            errors.append(ERROR101)
        if not string.strip(email):
            errors.append(ERROR104)
        if not string.strip(npass) or not string.strip(cpass):
            errors.append(ERROR103)
        if self.getUser(user) or (self._emergency_user and
                                  user == self._emergency_user.getUserName()):
            errors.append(ERROR105)
        if (npass or cpass) and (npass != cpass):
            errors.append(ERROR106)
        users = self.getUserNames()
        for n in users:
            us = self.getUser(n)
            if email.strip() == us.email:
                errors.append(ERROR113)
                break
            if fname == us.firstname and lname == us.lastname:
                errors.append(ERROR114)
                break
        if len(errors):
            if REQUEST is not None: 
                #save form data to session
                self.setUserSession(user, '', fname, lname, email)
                #save error to session
                self.setSessionErrors(errors)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                return errors
        n = Notification()
        template_text = self.notification.register.document_src()
        template_html = self.notification.register_html.document_src()
        if self.notification.register.title:
            subject = self.notification.register.title
        elif self.notification.register_html.title:
            subject = self.notification.register_html.title
        else:
            subject = "finShare notifications"
        if self.webmaster:
            webmaster = self.webmaster
        else:
            webmaster = "webmaster@finshare.it"
        n.send_registration(user, email, fname, lname, npass, webmaster, subject, template_text, template_html)
        if REQUEST is not None and REQUEST.has_key('destination'): 
            return REQUEST.RESPONSE.redirect(REQUEST['destination'] + '?save=ok')


    security.declarePublic('forgotPassword')
    def lostPassword(self, email='', REQUEST=None, RESPONSE=None):
        """ forgot password """
        errors = []
        if not string.strip(email):
            errors.append(ERROR104)
        pwd = fname = lname = accoount = None
        if email!='':
            for n in self.getUserNames():
                us = self.getUser(n)
                if email.strip() == us.email:
                    pwd = self.getUserPassword(us)
                    fname = self.getUserFirstName(us)
                    lname = self.getUserLastName(us)
                    account = self.getUserAccount(us)
                    break
            if pwd is None:
                errors.append(ERROR117)
        if len(errors):
            if REQUEST is not None: 
                #save form data to session
                self.setUserSession('', '', '', '', email)
                #save error to session
                self.setSessionErrors(errors)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                return errors
        n = Notification()
        template_text = self.notification.sendpassword.document_src()
        template_html = self.notification.sendpassword_html.document_src()
        if self.notification.sendpassword.title:
            subject = self.notification.sendpassword.title
        elif self.notification.sendpassword_html.title:
            subject = self.notification.sendpassword_html.title
        else:
            subject = "finShare notifications"
        if self.webmaster:
            webmaster = self.webmaster
        else:
            webmaster = "webmaster@finshare.it"
        n.send_passwords(account, email, fname, lname, pwd, webmaster, subject, template_text, template_html)
        if REQUEST is not None and REQUEST.has_key('destination'): 
            return REQUEST.RESPONSE.redirect(REQUEST['destination'] + '?save=ok')


    security.declarePublic('sendFeedback')
    def sendFeedback(self, title, comments, REQUEST=None):
        """ send feedback """
        n = Notification()
        template_text = self.notification.feedback.document_src()
        template_html = self.notification.feedback_html.document_src()
        user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        user_ob = self.getUser(user)
        fname = self.getUserFirstName(user_ob)
        lname = self.getUserLastName(user_ob)
        email = self.getUserEmail(user_ob)
        n.send_feedback(title, comments, fname, lname, email, self.getDocManagerURL(), 'c.nitu@finsiel.ro', template_text, template_html)
        if REQUEST is not None and REQUEST.has_key('destination'): 
            return REQUEST.RESPONSE.redirect(REQUEST['destination'] + '?send=ok')

    security.declareProtected(PERMISSION_EDIT_USERS, 'manage_delUsers')
    def manage_delUsers(self, users=[], REQUEST=None):
        """ """
        errors = []
        names = self.utConvertToList(users)
        if len(names) == 0:
            errors.append(ERROR108)
        if len(errors):
            #save error to session
            self.setSessionErrors(errors)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        self._doDelUsers(names)
        if REQUEST: return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER + '?save=ok')


    ###########################
    #       USER METHODS      #
    ###########################

    def getUserNames(self):
        """Return a list of usernames"""
        names=self.data.keys()
        names.sort()
        return names


    security.declareProtected(PERMISSION_EDIT_USERS, 'getUsersNames')
    def getUsersNames(self):
        """ return a list of usernames """
        return self.user_names()


    def getUsers(self):
        """Return a list of user objects"""
        data=self.data
        names=data.keys()
        names.sort()
        users=[]
        f=users.append
        for n in names:
            f(data[n])
        return users


    security.declarePublic('getUser') #xxx
    def getUser(self, name):
        """Return the named user object or None"""
        return self.data.get(name, None)


    def getUserAccount(self, user_obj):
        """ Return the username"""
        return user_obj.name


    def getUserPassword(self, user_obj):
        """ Return the password"""
        return user_obj.__


    def getUserFirstName(self, user_obj):
        """ Return the firstname"""
        return user_obj.firstname


    def getUserLastName(self, user_obj):
        """ Return the lastname"""
        return user_obj.lastname


    def getUserEmail(self, user_obj):
        """ Return the email """
        return user_obj.email


    def getUserRoles(self, user_obj):
        """ Return the user roles """
        return user_obj.roles


    def getUserHistory(self, user_obj):
        """ return the last login"""
        return user_obj.history


    def getUserCreatedDate(self, user_obj):
        """ Return the created date """
        return user_obj.created


    def getUserLastUpdated(self, user_obj):
        """ Return the lastupdated date"""
        return user_obj.lastupdated


    def getUserNotifications(self, user_obj):
        """ Return the lastupdated date"""
        return user_obj.notifications


    def forgotPassword(self, email, REQUEST=None, RESPONSE=None):
        """ retrieve user's password given the email """


    security.declareProtected(PERMISSION_EDIT_USERS, 'manage_users_html')
    manage_users_html = PageTemplateFile('zpt/DocAuth/show_users.zpt', globals())


    security.declareProtected(PERMISSION_EDIT_USERS, 'manage_addUser_html')
    manage_addUser_html = PageTemplateFile('zpt/DocAuth/add_user.zpt', globals())


    security.declareProtected(PERMISSION_EDIT_USERS, 'manage_editUser_html')
    manage_editUser_html = PageTemplateFile('zpt/DocAuth/edit_user.zpt', globals())


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'personal_html')
    personal_html = PageTemplateFile('zpt/DocAuth/personal.zpt', globals())


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'changepwd_html')
    changepwd_html = PageTemplateFile('zpt/DocAuth/changepwd.zpt', globals())


    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'newsletter_html')
    newsletter_html = PageTemplateFile('zpt/DocAuth/newsletter.zpt', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'feedback_html')
    feedback_html = PageTemplateFile('zpt/DocManager/DocManager_feedback', globals())

InitializeClass(DocAuthentication)