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
# The Original Code is Naaya version 1.0
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

#python imports
import re
import time
import string
from copy import copy

#zope imports
from OFS.PropertyManager import PropertyManager
from OFS.ObjectManager import ObjectManager
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUserFolder
from AccessControl.Permissions import view_management_screens, view, manage_users
from Globals import InitializeClass, PersistentMapping
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime

#product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import \
     string2object, object2string, InvalidStringError, file_utils, utils
from Products.NaayaCore.managers.session_manager import session_manager
from plugins_tool import plugins_tool
from User import User
from Role import Role

def manage_addAuthenticationTool(self, REQUEST=None):
    """ """
    ob = AuthenticationTool(ID_AUTHENTICATIONTOOL, TITLE_AUTHENTICATIONTOOL)
    self._setObject(ID_AUTHENTICATIONTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class AuthenticationTool(BasicUserFolder, Role, ObjectManager, session_manager, 
                         file_utils, plugins_tool, PropertyManager):

    meta_type = METATYPE_AUTHENTICATIONTOOL
    icon = 'misc_/NaayaCore/AuthenticationTool.gif'

    manage_options = (
        {'label': 'Users', 'action': 'manage_users_html'},
        {'label': 'Roles', 'action': 'manage_roles_html'},
        {'label': 'Permissions', 'action': 'manage_permissions_html'},
        {'label': 'Other sources', 'action': 'manage_sources_html'},
        {'label': 'Properties', 'action': 'manage_propertiesForm',
         'help': ('OFSP','Properties.stx')},
    )
    
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'encrypt_passwords', 'type': 'boolean', 'mode': 'w',
         'label': 'Encrypt users passwords'},
        {'id': 'email_expression', 'type': 'string', 'mode': 'w',
         'label': 'E-mail should match this regular expression'},
        {'id': 'email_confirmation', 'type': 'boolean', 'mode': 'w',
         'label': 'Ask for email confirmation before add user '},
    )
    
    security = ClassSecurityInfo()
    #
    # Properties
    #
    encrypt_passwords = False
    email_expression = '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}$'
    email_confirmation = False
    
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.data = PersistentMapping()
        Role.__dict__['__init__'](self)
        plugins_tool.__dict__['__init__'](self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

    security.declarePrivate('_doAddTempUser')
    def _doAddTempUser(self, **kwargs):
        """Generate a confirmation string, add it to temp users list, 
           and return it.
        """
        text = object2string(kwargs)
        if not hasattr(self, '_temp_users'):
            self._temp_users = []
        if text in self._temp_users:
            raise Exception, 'User already request access roles.'
        self._temp_users.append(text)
        self._p_changed = 1
        return text
        
    security.declarePrivate('_doAddUser')
    def _doAddUser(self, name, password, roles, domains, firstname, lastname, email, **kw):
        """Create a new user. The 'password' will be the
           original input password, unencrypted. This
           method is responsible for performing any needed encryption."""

        if password is not None and self.encrypt_passwords:
            password = self._encryptPassword(password)
        self.data[name] = User(name, password, roles, domains, firstname, lastname, email)
        self._p_changed = 1
        return name

    security.declarePrivate('_doChangeUser')
    def _doChangeUser(self, name, password, roles, domains, firstname, lastname, email, lastupdated, **kw):
        """Modify an existing user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""

        user=self.data[name]
        if password is not None:
            if self.encrypt_passwords and not self._isPasswordEncrypted(password):
                password = self._encryptPassword(password)
            user.__ = password
        user.roles = roles
        user.domains = domains
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.lastupdated = lastupdated
        self._p_changed = 1

    security.declareProtected(manage_users, 'getUserPass')
    def getUserPass(self):
        """Return a list of usernames"""
        temp = {}
        names=self.data.keys()
        for name in names:
            temp[name] = self.getUser(name).__
        return temp

    security.declarePrivate('_doChangeUserRoles')
    def _doChangeUserRoles(self, name, roles, **kw):
        """ """
        user=self.data[name]
        user.roles = roles
        self._p_changed = 1

    security.declarePrivate('_doDelUserRoles')
    def _doDelUserRoles(self, name, **kw):
        """ """
        for user in name:
            user_obj = self.data[user]
            user_obj.roles = []
        self._p_changed = 1

    security.declarePrivate('_doDelUsers')
    def _doDelUsers(self, names):
        """Delete one or more users."""

        for name in names:
            del self.data[name]
        self._p_changed = 1

    #zmi actions
    security.declareProtected(manage_users, 'manage_confirmUser')
    def manage_confirmUser(self, key='', REQUEST=None):
        """ Add user from key
        """
        if key not in getattr(self, '_temp_users', []):
            raise Exception, 'Invalid activation key !'
        try:
            res = string2object(key)
        except InvalidStringError, err:
            raise Exception, 'Invalid activation key !'
        else:
            self._temp_users.remove(key)
            self._doAddUser(**res)
            self._p_changed = 1
        if REQUEST: 
            REQUEST.RESPONSE.redirect('manage_users_html')
        return res
        
    security.declareProtected(manage_users, 'manage_addUser')
    def manage_addUser(self, name='', password='', confirm='', roles=[], domains=[], firstname='',
        lastname='', email='', strict=0, REQUEST=None, **kwargs):
        """ """
        # Verify captcha
        captcha_gen_word = self.getSession('captcha', '')
        captcha_prov_word = kwargs.get('verify_word', captcha_gen_word)
        if captcha_prov_word != captcha_gen_word:
            raise Exception, 'The word you typed does not match with the one shown in the image. Please try again.'
        if not firstname:
            raise Exception, 'The first name must be specified'
        if not lastname:
            raise Exception, 'The last name must be specified'
        if not email:
            raise Exception, 'The email must be specified'
        if getattr(self, 'email_expression', ''):
            email_expr = re.compile(self.email_expression, re.IGNORECASE)
            if not re.match(email_expr, email):
                raise Exception, 'Invalid email address.'
        if not name:
            raise Exception, 'An username must be specified'
        if not password or not confirm:
            raise Exception, 'Password and confirmation must be specified'
        if self.getUser(name) or (self._emergency_user and name == self._emergency_user.getUserName()):
            raise Exception, 'A user with the specified name already exists'
        if (password or confirm) and (password != confirm):
            raise Exception, 'Password and confirmation do not match'
        if strict:
            users = self.getUserNames()
            for n in users:
                us = self.getUser(n)
                if email.strip() == us.email:
                    raise Exception, 'A user with the specified email already exists, username %s' % n
                if firstname == us.firstname and lastname == us.lastname:
                    raise Exception, 'A user with the specified name already exists, username %s' % n
        #convert data
        roles = self.utConvertToList(roles)
        domains = self.utConvertToList(domains)
        #
        # Confirm by mail
        #
        if self.emailConfirmationEnabled():
            user = self._doAddTempUser(name=name, password=password, roles=roles, 
                                       domains=domains, firstname=firstname, 
                                       lastname=lastname, email=email)
            
        else:
            user = self._doAddUser(name, password, roles, domains, 
                                   firstname, lastname, email)
        if REQUEST: 
            REQUEST.RESPONSE.redirect('manage_users_html')
        return user

    security.declareProtected(manage_users, 'manage_changeUser')
    def manage_changeUser(self, name='', password='', confirm='', roles=[], domains=[], firstname='',
        lastname='', email='', REQUEST=None):
        """ """
        if password == '' and confirm == '':
            password = confirm = None
        if not firstname:
            raise Exception, 'The first name must be specified'
        if not lastname:
            raise Exception, 'The last name must be specified'
        if not email:
            raise Exception, 'The email must be specified'
        if not name:
            raise Exception, 'An username must be specified'
        if not self.getUser(name):
            raise Exception, 'Unknown user'
        if (password or confirm) and (password != confirm):
            raise Exception, 'Password and confirmation do not match'
        #convert data
        user_ob = self.getUser(name)
        roles = self.getUserRoles(user_ob)
        domains = user_ob.getDomains()
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(name, password, roles, domains, firstname, lastname, email, lastupdated)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_users_html')

    security.declareProtected(manage_users, 'manage_addUsersRoles')
    def manage_addUsersRoles(self, name='', roles=[], loc='allsite', location='', REQUEST=None):
        """ """
        if not name:
            raise Exception, 'An username must be specified'
        if not roles:
            raise Exception, 'No roles were specified'
        if loc == 'allsite':
            location = ''
        elif loc == 'other':
            location = location
            location_obj = self.unrestrictedTraverse(location, None)
            if location_obj is None:
                raise Exception, 'Invalid location'
        #convert data
        roles = self.utConvertToList(roles)
        if location == '':
            self._doChangeUserRoles(name, roles)
        else:
            location_obj.manage_setLocalRoles(name, roles)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_userRoles_html')

    security.declareProtected(manage_users, 'manage_revokeUsersRoles')
    def manage_revokeUsersRoles(self, roles=[], REQUEST=None):
        """ """
        roles = self.utConvertToList(roles)
        for role in roles:
            users_roles = string.split(role, '||')
            user = self.utConvertToList(users_roles[0])
            location = users_roles[1]
            location_obj = self.utGetObject(location)
            if location == '':
                self._doDelUserRoles(user)
            else:
                location_obj.manage_delLocalRoles(user)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_userRoles_html')

    security.declareProtected(manage_users, 'manage_delUsers')
    def manage_delUsers(self, names=[], REQUEST=None):
        """ """
        self._doDelUsers(self.utConvertToList(names))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_users_html')

    security.declareProtected(manage_users, 'getUserNames')
    def getUserNames(self):
        """Return a list of usernames"""
        names=self.data.keys()
        names.sort()
        return names

    security.declareProtected(manage_users, 'getUserNamesSortedByAttr')
    def getUserNamesSortedByAttr(self, skey='', rkey=0):
        """Return a list of usernames sorted by a specified attribute"""
        if not skey or skey=='__':skey = 'name'
        users_obj=self.data.values()
        users_obj = utils().utSortObjsListByAttr(users_obj,skey,rkey)
        res=[]
        for user_obj in users_obj:
            res.append(user_obj.name)
        return res

    security.declareProtected(manage_users, 'getUsersRolesRestricted')
    def getUsersRolesRestricted(self, path):
        """
        Returns information about the user's roles inside the given path.
        """
        users_roles = {}
        for folder in self.getCatalogedObjects(meta_type=[METATYPE_FOLDER,'Folder'], has_local_role=1, path=path):
            for roles_tuple in folder.get_local_roles():
                local_roles = self.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] in self.user_names() and len(local_roles) > 0:
                    if not users_roles.has_key(str(roles_tuple[0])):
                        users_roles[str(roles_tuple[0])] = []
                    users_roles[str(roles_tuple[0])].append((local_roles, folder.absolute_url(1)))
        return users_roles

    security.declareProtected(manage_users, 'searchUsers')
    def searchUsers(self, query, limit=0):
        """ search users """
        if query:
            users = []
            users_a = users.append
            for user in self.getUsers():
                if user.name.find(self.utToUtf8(query))!=-1 or user.email.find(self.utToUtf8(query))!=-1 or \
                        user.firstname.find(self.utToUtf8(query))!=-1 or user.lastname.find(self.utToUtf8(query))!=-1:
                    users_a((user.name, '%s %s' % (user.firstname, user.lastname), user.email))
            if limit and len(users) > int(limit):
                return 0, []
            else:
                return 1, users
        else:
            return 2, []

    security.declareProtected(manage_users, 'isNewUser')
    def isNewUser(self, user_obj, days=5):
        """ check if the user is recently added """
        if DateTime() - DateTime(self.getUserCreatedDate(user_obj)) <= 5:
            return True
        else:
            return False

    security.declareProtected(view, 'isLocalUser')
    def isLocalUser(self, REQUEST=None):
        """ check if authenticated user is stored localy """
        if REQUEST.AUTHENTICATED_USER.getUserName() in self.getUserNames():
            return 1
        return 0

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

    security.declareProtected(view, 'getUser')
    def getUser(self, name):
        """Return the named user object or None"""
        return self.data.get(name, None)

    def getAuthenticatedUserRoles(self, p_meta_types=None):
        """
        Returns a list with all roles of the authenticated user.
        """
        if p_meta_types is None: p_meta_types = self.get_containers_metatypes()
        r = []
        ra = r.append
        user = self.REQUEST.AUTHENTICATED_USER
        username = user.getUserName()
        userroles = self.utConvertToList(self.getUserRoles(user))
        for x in ['Anonymous', 'Authenticated', 'Owner']:
            if x in userroles:
                userroles.remove(x)
        if len(userroles): ra((userroles, ''))
        folders = self.getCatalogedObjects(meta_type=p_meta_types, has_local_role=1)
        folders.insert(0, self.getSite())
        for folder in folders:
            for roles_tuple in folder.get_local_roles():
                local_roles = self.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] == username and len(local_roles) > 0:
                    ra((local_roles, folder.absolute_url(1)))
        return r

    def getUsersRoles(self, p_meta_types=None):
        """ """
        if p_meta_types is None: p_meta_types = self.get_containers_metatypes()
        users_roles = {}
        for username in self.user_names():   #get the users
            user = self.getUser(username)
            users_roles[username] = [(self.getUserRoles(user), '')]

        for folder in self.getCatalogedObjects(meta_type=p_meta_types, has_local_role=1):
            for roles_tuple in folder.get_local_roles():
                local_roles = self.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] in self.user_names() and len(local_roles) > 0:
                    users_roles[str(roles_tuple[0])].append((local_roles, folder.absolute_url(1)))
        return users_roles

    security.declareProtected(manage_users, 'getUsersWithRoles')
    def getUsersWithRoles(self):
        """ return the users with their roles """
        users = {}
        for k, v in self.getUsersRoles().items():
            if (len(v) > 1 and len(v[1][0]) > 0) or (len(v) == 1 and len(v[0][0]) > 0):
                users[k] = v
        return users

    def getUserSource(self, user):
        """ given a user returns the source """
        user_ob = self.getUser(user)
        if user_ob:
            return 'acl_users'
        else:
            #check sources
            for source in self.getSources():
                source_acl = source.getUserFolder()
                user_ob = source_acl.getUser(user)
                if user_ob:
                    return source.title
            return 'n/a'

    security.declareProtected(manage_users, 'getUsersFullNames')
    def getUsersFullNames(self, users):
        """
        Given a list of users ids it returns the list with their names.
        A lookup will be made against the portal users folder and also
        in against all the sources.
        """
        r = []
        ra = r.append
        buf = copy(users)
        #first check local users
        local_users = self.user_names()
        for user in users:
            if user in local_users:
                name = self.getUserFullName(self.getUser(user))
                if name is not None: ra(name)
                buf.remove(user)
        if len(buf):
            buf1 = copy(buf)
            #check sources
            for source in self.getSources():
                source_acl = source.getUserFolder()
                for user in buf:
                    name = source.getUserFullName(user, source_acl)
                    if name is not None: ra(name)
                    buf1.remove(user)
                    if len(buf1)==0: break
        return r

    security.declareProtected(manage_users, 'getUsersEmails')
    def getUsersEmails(self, users):
        """
        Given a list of users ids it returns the list with their emails.
        A lookup will be made against the portal users folder and also
        in against all the sources.
        """
        r = []
        ra = r.append
        buf = copy(users)
        #first check local users
        local_users = self.user_names()
        for user in users:
            if user in local_users:
                email = self.getUserEmail(self.getUser(user))
                if email is not None: ra(email)
                buf.remove(user)
        if len(buf):
            buf1 = copy(buf)
            #check sources
            for source in self.getSources():
                source_acl = source.getUserFolder()
                for user in buf:
                    email = source.getUserEmail(user, source_acl)
                    if email is not None: ra(email)
                    buf1.remove(user)
                    if len(buf1)==0: break
        return r

    def getUserAccount(self, user_obj):
        """ Return the username"""
        return user_obj.name

    def getUserPassword(self, user_obj):
        """ Return the password"""
        return user_obj.__

    def getUserRoles(self, user_obj):
        """ Return the user roles """
        return user_obj.roles

    def getUserFirstName(self, user_obj):
        """ Return the firstname"""
        return user_obj.firstname

    def getUserLastName(self, user_obj):
        """ Return the lastname"""
        return user_obj.lastname

    def getUserFullName(self, user_obj):
        """ Return the full name of the user """
        return '%s %s' % (user_obj.firstname, user_obj.lastname)

    def getUserFullNameByID(self, user_str):
        """ Return the full name of the user """
        user_obj = self.getUser(user_str)
        if user_obj is not None:
            return user_obj.firstname + ' ' + user_obj.lastname
        else:
            return user_str

    def getUserEmail(self, user_obj):
        """ Return the email """
        return user_obj.email

    def getUserHistory(self, user_obj):
        """ return the last login"""
        return user_obj.history

    def getUserCreatedDate(self, user_obj):
        """ Return the created date """
        return user_obj.created

    def getUserLastUpdated(self, user_obj):
        """ Return the lastupdated date"""
        return user_obj.lastupdated

    def getSuperUserFolders(self):
        #return s list with user folders
        ufs = self.superValues(self.getKnownMetaTypes())
        if self in ufs: ufs.remove(self)
        return ufs

    def getSources(self):
        #returns a list with all sources
        return map(self._getOb, map(lambda x: x['id'], self._objects))

    def getSourceObj(self, p_source_id):
        #returns a source object
        try: return self._getOb(p_source_id)
        except: return None

    security.declareProtected(manage_users, 'managePlugins')
    def managePlugins(self, REQUEST=None):
        """ Refresh the list of available plugins """
        self.loadPlugins()
        if REQUEST: REQUEST.RESPONSE.redirect('manage_sources_html')

    def manageAddSource(self, source_path, title='', REQUEST = None):
        """ """
        source_obj = self.unrestrictedTraverse('/' + source_path, None)
        plugin_obj = self.getPluginInstance(source_obj.meta_type)
        id = self.utGenRandomId()
        plugin_obj.id = id
        plugin_obj.obj_path = source_path
        plugin_obj.title = title
        self._setObject(id, plugin_obj)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_sources_html')

    security.declareProtected(manage_users, 'emailConfirmationEnabled')
    def emailConfirmationEnabled(self):
        # Check to see if email confirmation is enabled
        if self.isAnonymousUser():
            return self.email_confirmation
        # No email confirmation need if user is not anonymous
        return False
    
    def manageDeleteSource(self, id, REQUEST = None):
        """ """
        try: self._delObject(id)
        except: pass
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_sources_html')

    manage_users_html = PageTemplateFile('zpt/authentication_content', globals())
    manage_addUser_html = PageTemplateFile('zpt/authentication_adduser', globals())
    manage_editUser_html = PageTemplateFile('zpt/authentication_edituser', globals())

    manage_permissions_html = PageTemplateFile('zpt/authentication_permissions', globals())
    manage_addPermission_html = PageTemplateFile('zpt/authentication_addpermission', globals())
    manage_editPermission_html = PageTemplateFile('zpt/authentication_editpermission', globals())

    manage_roles_html = PageTemplateFile('zpt/authentication_roles', globals())
    manage_addRole_html = PageTemplateFile('zpt/authentication_addrole', globals())
    manage_editRole_html = PageTemplateFile('zpt/authentication_editrole', globals())

    manage_userRoles_html = PageTemplateFile('zpt/authentication_user_roles', globals())
    sitemap = PageTemplateFile('zpt/authentication_sitemap', globals())

    manage_sources_html = PageTemplateFile('zpt/authentication_sources', globals())
    manage_source_html = PageTemplateFile('zpt/authentication_source', globals())

InitializeClass(AuthenticationTool)
