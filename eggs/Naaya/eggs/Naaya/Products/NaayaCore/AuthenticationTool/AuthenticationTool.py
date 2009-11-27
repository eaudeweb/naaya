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
from copy import copy, deepcopy
from StringIO import StringIO
import csv

#zope imports
from OFS.PropertyManager import PropertyManager
from OFS.ObjectManager import ObjectManager
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUserFolder
from AccessControl.User import SpecialUser
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
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS


def manage_addAuthenticationTool(self, REQUEST=None):
    """ """
    ob = AuthenticationTool(ID_AUTHENTICATIONTOOL, TITLE_AUTHENTICATIONTOOL)
    self._setObject(ID_AUTHENTICATIONTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

def check_username(name):
    name_expr = re.compile('^[A-Za-z0-9]*$')
    return re.match(name_expr, name)

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

    security.declarePublic('changeLastLogin')
    def changeLastLogin(self, name):
        user=self.data.get(name, None)
        if user:
            user.lastlogin = time.strftime('%d %b %Y %H:%M:%S')
            self._p_changed = 1

    security.declarePublic('changeLastPost')
    def changeLastPost(self, name):
        user=self.data.get(name, None)
        if user:
            user.lastpost = time.strftime('%d %b %Y %H:%M:%S')
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
        if not check_username(name):
            raise Exception, 'Username: only letters and numbers allowed'
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
        """
        Return a list of userids of all users registered in this portal.
        """
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
        Returns information about all the users' roles inside the given path.
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
        """
        Search `query` in all users' first/last/full names and emails
        TODO: refactor
        """
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
        """
        return True if user was created in the last 5 days
        note: the `days` parameter is not used.
        """
        if DateTime() - DateTime(self.getUserCreatedDate(user_obj)) <= 5:
            return True
        else:
            return False

    security.declareProtected(view, 'isLocalUser')
    def isLocalUser(self, REQUEST=None):
        """
        Return 1 if the current user is registered in this user folder,
        0 otherwise
        """
        if REQUEST.AUTHENTICATED_USER.getUserName() in self.getUserNames():
            return 1
        return 0

    def getUsers(self):
        """
        Return all user objects registered in this user folder
        """
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
        """
        Return the user object for the specified userid ( None if not found)
        """
        return self.data.get(name, None)

    def get_ldap_group_roles(self, name, source):
        acl_groups = source.get_mapped_groups()
        roles = []
        for group in acl_groups:
            if source.user_in_group(name, group):
                roles.extend(source.get_group_roles(group))
        return roles

    def authenticate(self, name, password, request):
        # return local defined user if it exists
        user = super(AuthenticationTool, self).authenticate(name, password, request)
        if user is not None:
            return user
        # otherwise start looking in LDAP sources
        # TODO: this should be done individually in each source type (if we'll have more than LDAP)
        for source in self.getSources():
            user = source.getUserFolder().authenticate(name, password, request)
            if user is not None and not isinstance(user, SpecialUser):
                user = deepcopy(user) #we make a copy so the new roles are not cached in the root acl_users
                try:
                    user.roles.extend([x for x in self.get_ldap_group_roles(name, source) if x not in user.roles])
                # roles is not a list, roles remain unchanged
                # this will happen when the LDAP user folder is
                # replaced with a Zope UserFolder
                except AttributeError:
                    return None
                return user

    def getAuthenticatedUserRoles(self, p_meta_types=None):
        """
        Returns a list with all roles of the authenticated user.

        This function looks at the site level, then inside all folders for
        local roles.
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

    def isAdministrator(self, path=''):
        """
        Check if the current user has Administrator role at the specified
        path (by default, at the site level)
        """
        list_roles = self.getAuthenticatedUserRoles()
        for roles, path in list_roles:
            if (('Manager' in roles) or ('Administrator' in roles)) and path == '':
                return True
            elif (('Manager' in roles) or ('Administrator' in roles)) and path == path:
                return True
        return False

    def getUsersRoles(self, p_meta_types=None):
        """
        Same as getAuthenticatedUserRoles, except for all the users registered
        in this folder. Don't use this in new code.

        Output format: a dict with keyes=userids and values=list of roles. The
        list of roles contains tuples of (list of role names, path of folder).
        """
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
        """
        Honestly, we're stumped. Don't use this in new code.
        """
        users = {}
        for k, v in self.getUsersRoles().items():
            if (len(v) > 1 and len(v[1][0]) > 0) or (len(v) == 1 and len(v[0][0]) > 0):
                users[k] = v
        return users

    security.declareProtected(manage_users, 'getUsersWithRole')
    def getUsersWithRole(self, role):
        """
        Don't use this in new code.
        return the user objects that have the specified role
        """
        local_users = self.getUsersWithRoles()
        #dictionary that will hold local users
        local_result = {}
        for user_id, roles in local_users.items():
            for location in roles:
                if role in location[0]:
                    if user_id not in local_result.keys():
                        user_obj = self.getUser(user_id)
                        user_name = "%s %s" % (self.getUserFirstName(user_obj), self.getUserLastName(user_obj))
                        user_email = self.getUserEmail(user_obj)
                        local_result[user_id] = {'name': user_name, 'email': user_email}


        #dictionary that will hold external users
        external_users = {}
        for source in self.getSources():
            source_obj = self.getSourceObj(source.getId())
            users = source_obj.getSortedUserRoles(skey='user')
            for user in users:
                user_roles = user[3]
                for user_role in user_roles:
                    if role in user_role[0]:
                        user_id = user[0]
                        user_name = user[1]
                        user_email = source_obj.getUserEmail(user_id, source_obj.getUserFolder())
                        external_users[user_id] = {'name': user_name, 'email': user_email}

        #add external users data to local_result
        local_result.update(external_users)
        #and return everything
        return local_result

    def getUserSource(self, user):
        """
        Returns information about where a user is registered:
         - if it's inside this user folder, return 'acl_users'
         - if it's in a known external source, returns the source's title
         - otherwise returns 'n/a'
        """
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

    security.declarePrivate('get_user_with_userid')
    def get_user_with_userid(self, userid):
        """
        Search for a user with the given ID, in this user folder and
        external sources. Returns None if user not found, or is anonymous.
        """
        if userid is None:
            return None

        if userid in self.user_names():
            return self.getUser(userid)

        for source in self.getSources():
            user = source.getUserFolder().getUser(userid)
            if user is not None:
                return user

        return None

    security.declarePrivate('name_from_userid')
    def name_from_userid(self, userid):
        """
        Given a userid, try to get its full name. If userid is None then we
        assume it's an anonymous user, and return `"Anonymous User"`. If we
        can't find the user, return an empty string.
        """
        if userid is None:
            return "Anonymous User"

        if userid in self.user_names():
            return self.getUserFullName(self.getUser(userid))

        for source in self.getSources():
            source_acl = source.getUserFolder()
            name = source.getUserFullName(userid, source_acl)
            if name is not None:
                return name

        return ''

    security.declarePrivate('get_current_userid')
    def get_current_userid(self):
        """
        Get the userid of the currently logged-in user. Returns `None` if
        the current user is anonymous.
        """
        if self.isAnonymousUser():
            return None
        else:
            return self.REQUEST.AUTHENTICATED_USER.getId()

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
        """
        Given a user object, returns the name inside
        """
        return user_obj.name

    def getUserPassword(self, user_obj):
        """
        Given a user object, returns the password inside
        """
        return user_obj.__

    def getUserRoles(self, user_obj):
        """
        Given a user object, returns the roles inside
        """
        return user_obj.roles

    security.declarePrivate('get_all_user_roles')
    def get_all_user_roles(self, uid):
        """
        Given a userid, returns all the roles of that user, looking at this
        user folder and any external sources.
        """
        # check local users
        roles = []
        local_user = self.getUser(uid)
        if local_user is not None:
            return local_user.roles
        # check ldap users and groups
        for source in self.getSources():
            # users
            portal_roles = source.getUsersRoles(source.getUserFolder()).get(uid, [])
            if portal_roles:
                for role, location in portal_roles:
                    if location == self.getSite().absolute_url(1):
                        roles.extend(role)
            # groups
            roles.extend(self.get_ldap_group_roles(uid, source))

        if self.REQUEST is not None:
            auth_user = self.REQUEST['AUTHENTICATED_USER']
            roles.extend(auth_user.getRoles())
        return roles

    def getUserFirstName(self, user_obj):
        """
        Given a user object, returns the first name
        """
        return user_obj.firstname

    def getUserLastName(self, user_obj):
        """
        Given a user object, returns the last name
        """
        return user_obj.lastname

    def getUserFullName(self, user_obj):
        """
        Given a user object, returns the concatenation of first+last names
        """
        try:
            return '%s %s' % (user_obj.firstname, user_obj.lastname)
        except AttributeError:
            return ''

    def getUserFullNameByID(self, user_str):
        """
        Just like getUserFullName, but receives userid as parameter, and
        only works for locally registered users
        """
        user_obj = self.getUser(user_str)
        if user_obj is not None:
            return user_obj.firstname + ' ' + user_obj.lastname
        else:
            return user_str

    def getUserEmail(self, user_obj):
        """
        Given a user object, returns the email
        """
        try:
            return user_obj.email
        except AttributeError:
            # This can happen when the LDAP user folder maps the LDAP
            # attribute to the "mail" Python attribute, because other
            # Zope products depend on the "mail"  attribute.
            return user_obj.mail

    def getUserHistory(self, user_obj):
        """ Given a user object, returns its `history` property """
        return user_obj.history

    def getUserCreatedDate(self, user_obj):
        """ Given a user object, returns its `created` property """
        return user_obj.created

    def getUserLastUpdated(self, user_obj):
        """ Given a user object, returns its `lastupdated` property """
        return user_obj.lastupdated

    def getUserLastLogin(self, user_obj):
        """ Given a user object, returns its `lastlogin` property """
        return user_obj.lastlogin

    def getUserLastPost(self, user_obj):
        """ Given a user object, returns its `lastpost` property """
        return user_obj.lastpost

    def getSuperUserFolders(self):
        #return s list with user folders
        ufs = self.superValues(self.getKnownMetaTypes())
        if self in ufs: ufs.remove(self)
        return ufs

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSources')
    def getSources(self):
        """
        returns a list with all registered external sources
        """
        return map(self._getOb, map(lambda x: x['id'], self._objects))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSourceObj')
    def getSourceObj(self, p_source_id):
        """
        returns a source object
        """
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
        """
        Check to see if email confirmation is enabled
        """
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

    def showBulkDownloadButton(self):
        """ """
        return self.checkPermissionPublishObjects()

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'downloadUsersCsv')
    def downloadUsersCsv(self, REQUEST=None, RESPONSE=None):
        """ Return a csv file as a session response.
        """
        if not (REQUEST and RESPONSE):
            return ""

        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        output = StringIO()
        csv_writer = csv.writer(output)
        csv_writer.writerow(['Account', 'User', 'Full name', 'Email address', 'LDAP Group', 'LDAP Roles'])

        local_users = self.getUsers()
        for user in local_users:
            user_info = []

            user_info.append(u'Local')

            user_info.append(unicode(user).encode('utf-8'))

            full_name = self.getUserFirstName(user) + ' ' + self.getUserLastName(user)
            if isinstance(full_name, unicode):
                full_name = full_name.encode('utf-8')
            user_info.append(full_name)

            email = self.getUserEmail(user)
            user_info.append(unicode(email).encode('utf-8'))

            csv_writer.writerow(user_info)

        ldap_sources = self.getSources()
        for source in ldap_sources:
            acl = source.getUserFolder()
            for user, roles in source.getUsersRoles(acl).items():
                user_info = []

                user_info.append(u'LDAP (source_id=%s)' % source.id)

                user_info.append(user)

                full_name = source.getUserFullName(user, acl)
                user_info.append(full_name)

                email = source.getUserEmail(user, acl)
                user_info.append(email)

                group = source.getUserLocation(user)
                user_info.append(group)

                roles_info = ' | '.join([', '.join(role[0]) + ' on ' + role[1] for role in roles])
                user_info.append(unicode(roles_info).encode('utf-8'))

                csv_writer.writerow(user_info)

        RESPONSE.setHeader('Content-Type', 'text/csv; charset=utf-8')
        RESPONSE.setHeader('Content-Length', output.len)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        RESPONSE.setHeader('Content-Disposition', "inline; filename*=UTF-8''users.csv")

        return output.getvalue()

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
