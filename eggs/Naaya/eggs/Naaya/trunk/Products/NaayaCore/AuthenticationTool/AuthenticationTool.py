"""
This tool is used to manage users in Naaya Site. Users can come from
remote (LDAP) or local sources. This tool also provides utilities for managing
user roles, role permissions and searching.

"""

from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view, manage_users
from AccessControl.User import BasicUserFolder
from AccessControl.User import SimpleUser
from App.ImageFile import ImageFile
from DateTime import DateTime
from Globals import InitializeClass, PersistentMapping
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from Products.Naaya.interfaces import INySite
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaBase.interfaces import IRoleLogger
from Products.NaayaCore.AuthenticationTool.events import RoleAssignmentEvent
from Products.NaayaCore.AuthenticationTool.recover_password import RecoverPassword
from Products.NaayaCore.constants import ID_AUTHENTICATIONTOOL
from Products.NaayaCore.constants import METATYPE_AUTHENTICATIONTOOL
from Products.NaayaCore.constants import METATYPE_FOLDER
from Products.NaayaCore.constants import TITLE_AUTHENTICATIONTOOL
from Products.NaayaCore.constants import DISABLED_EMAIL
from Products.NaayaCore.managers.import_export import UnicodeReader
from Products.NaayaCore.managers.import_export import set_response_attachment
from Products.NaayaCore.managers.session_manager import session_manager
from Products.NaayaCore.managers.utils import InvalidStringError, file_utils, utils
from Products.NaayaCore.managers.utils import string2object, object2string
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Role import Role
from StringIO import StringIO
from User import User
from copy import copy
from naaya.core.exceptions import ValidationError, i18n_exception
from naaya.core.utils import force_to_unicode
from naaya.core.utils import is_valid_email
from naaya.core.zope2util import relative_object_path, get_zope_env
from persistent.list import PersistentList
from plugins_tool import plugins_tool
from warnings import warn
from zope.event import notify
import csv
import logging
import re
import time

log = logging.getLogger(__name__)

def manage_addAuthenticationTool(self, REQUEST=None):
    """ """
    ob = AuthenticationTool(ID_AUTHENTICATIONTOOL, TITLE_AUTHENTICATIONTOOL)
    self._setObject(ID_AUTHENTICATIONTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

def check_username(name):
    name_expr = re.compile(r'^[A-Za-z0-9._-]+$')
    return re.match(name_expr, name)

def is_anonymous(user_obj):
    """ check if the given user is `anonymous` (i.e. not authenticated) """
    if user_obj is None or user_obj.getUserName() == 'Anonymous User':
        return True
    else:
        return False

class DummyUser(SimpleUser):
    """ Wrapper for User Sources. It is used for user searchs
    This object should go away when the Local users have the same api and
    properties with other user sources.

    Author: Alexandru Plugaru
    """
    mapping = {
        'getUserFirstName': 'firstname',
        'getUserLastName': 'lastname',
        'getUserEmail': 'email',
    }
    created = DateTime(1970, 1, 1)
    map = None

    def __init__(self, **kw):
        for key, val in kw.items():
            setattr(self, key, val)

    def __getattr__(self, name):
        """ This """
        if name in self.mapping.keys():
            return getattr(self, self.map[name])
        else:
            return getattr(super(DummyUser, self), name)
    def getRoles(self):
        roles = []
        for role in self.roles:
            if isinstance(role, (tuple, list)):
                for r  in role[0]:
                    roles.append(r)
            else:
                roles.append(role)
        return roles
    def getUserCreatedDate(self):
        return self.created


class UserInfo(object):
    """
    Encapsulate information about a user: name, email, etc.  While various
    functions in Naaya's authentication code return latin-1 or utf-8 encoded
    bytestrings, UserInfo has field values as unicode strings.

    Common fields: `first_name`, `last_name`, `full_name`, `user_id`,
    `email`, `organisation`.

    Other fields: `_get_zope_user` (callable that returns the Zope user
    object), `_source` (the user source where this user was found).
    """
    mandatory_fields = set(['user_id', 'first_name', 'last_name', 'full_name',
                            'email', '_get_zope_user', '_source'])

    def __init__(self, **fields):
        missing_fields = self.mandatory_fields - set(fields)
        assert not missing_fields, "Missing fields: %r" % list(missing_fields)

        # we may want to comment this out for speed reasons
        assert isinstance(fields.get('user_id', None), str),\
               "user_id %r must be str" % fields['user_id']
        for key, value in fields.iteritems():
            if key in ['user_id', '_get_zope_user', '_source', 'jpegPhoto']:
                continue
            assert isinstance(value, unicode), \
                   ("value %r (for %r, user %r) not unicode" %
                   (value, key, fields['user_id']))

        self.__dict__.update(fields)

    @property
    def zope_user(self):
        """
        Fetch the corresponding Zope user that can be used in authorization.
        """
        # `_get_zope_user` was given to us by our factory. It's a callable, and
        # not the actual user, because it may be costly to obtain (e.g. from
        # an LDAP database).
        return self._get_zope_user()


class LocalUserInfo(UserInfo):
    """ UserInfo subclass for local users """


class AuthenticationTool(BasicUserFolder, Role, ObjectManager, session_manager,
                         file_utils, plugins_tool, PropertyManager):

    meta_type = METATYPE_AUTHENTICATIONTOOL
    icon = 'misc_/NaayaCore/AuthenticationTool.gif'

    manage_options = (
        {'label': 'Users', 'action': 'manage_users_html'},
        {'label': 'Other sources', 'action': 'manage_sources_html'},
        {'label': 'Properties', 'action': 'manage_propertiesForm',
         'help': ('OFSP','Properties.stx')},
        {'label': 'Sending email log',
         'action': 'manage_send_emails_log_html'},
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
    admin_js = ImageFile('www/admin.js', globals())

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.data = PersistentMapping()

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
            raise ValidationError, 'User already request access roles.'
        self._temp_users.append(text)
        self._p_changed = 1
        return text

    security.declarePrivate('_doAddUser')
    def _doAddUser(self, name, password, roles, domains, firstname, lastname,
                    email, **kw):
        """Create a new user. The 'password' will be the
           original input password, unencrypted. This
           method is responsible for performing any needed encryption."""

        if password is not None and self.encrypt_passwords:
            password = self._encryptPassword(password)
        self.data[name] = User(name, password, roles, domains, firstname,
                    lastname, email)
        log.info('User %s, email:%s added.', name, email)
        self._p_changed = 1
        return name

    security.declarePrivate('_doChangeUser')
    def _doChangeUser(self, name, password, roles, domains, firstname,
                lastname, email, lastupdated, **kw):
        """Modify an existing user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""

        user=self.data[name]
        if password is not None:
            if (self.encrypt_passwords and
                not self._isPasswordEncrypted(password)):
                password = self._encryptPassword(password)
            user.__ = password
        user.setRoles(self.getSite(), roles)
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
        user.setRoles(self.getSite(), roles)
        self._p_changed = 1

    security.declarePrivate('_doDelUserRoles')
    def _doDelUserRoles(self, name, **kw):
        """ """
        for user in name:
            user_obj = self.data[user]
            user_obj.delRoles(self.getSite())
        self._p_changed = 1

    security.declarePrivate('_doDelUsers')
    def _doDelUsers(self, names):
        """Delete one or more users."""

        #Delete local roles (from folder property)
        users_roles = self.getUsersRoles()
        for user, roles in users_roles.iteritems():
            if user not in names:
                continue
            for pair in roles:
                if not pair[0]:
                    continue
                location = self.utGetObject(pair[1])
                if location is not None:
                    location.manage_delLocalRoles([user])

        for name in names:
            del self.data[name]

        self._p_changed = True

    #zmi actions
    security.declareProtected(manage_users, 'manage_confirmUser')
    def manage_confirmUser(self, key='', REQUEST=None):
        """ Add user from key
        """
        if key not in getattr(self, '_temp_users', []):
            raise ValidationError, 'Invalid activation key !'
        try:
            res = string2object(key)
        except InvalidStringError:
            raise ValidationError, 'Invalid activation key !'
        else:
            self._temp_users.remove(key)
            self._doAddUser(**res)
            self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_users_html')
        return res

    security.declareProtected(manage_users, 'manage_addUser')
    def manage_addUser(self, name='', password='', confirm='', roles=[],
                domains=[], firstname='', lastname='', email='', strict=0,
                REQUEST=None):
        """ """
        email = email.strip()
        if not check_username(name):
            raise ValidationError, 'Username: only letters and numbers allowed'
        if not firstname:
            raise ValidationError, 'The first name must be specified'
        if not lastname:
            raise ValidationError, 'The last name must be specified'
        if not email:
            raise ValidationError, 'The email must be specified'
        if not is_valid_email(email):
            raise ValidationError, 'Invalid email address.'
        if not name:
            raise ValidationError, 'A username must be specified'
        if not password or not confirm:
            raise ValidationError, 'Password and confirmation must be specified'

        name = str(name)

        existing_usernames = set(username.lower
            for username in self.getUserNames())
        if self.get_user_with_userid(name) is not None or name.lower() in existing_usernames:
            raise i18n_exception(ValidationError,
                                 'Username ${user} already in use', user=name)
        if (password or confirm) and (password != confirm):
            raise ValidationError, 'Password and confirmation do not match'
        if strict:
            users = self.getUserNames()
            for n in users:
                us = self.getUser(n)
                if email.lower() == us.email.lower():
                    raise i18n_exception(ValidationError,
                            'A user with the specified email already exists, '
                            'username ${user}', user=n)
        #convert data
        roles = self.utConvertToList(roles)
        domains = self.utConvertToList(domains)
        #
        # Confirm by mail
        #
        if self.emailConfirmationEnabled():
            user = self._doAddTempUser(name=name, password=password,
                                       roles=roles, domains=domains,
                                       firstname=firstname, lastname=lastname,
                                       email=email)

        else:
            user = self._doAddUser(name, password, roles, domains,
                                   firstname, lastname, email)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_users_html')
        return user

    security.declareProtected(manage_users, 'manage_changeUser')
    def manage_changeUser(self, name='', password='', confirm='', roles=[],
                          domains=[], firstname='', lastname='', email='',
                          REQUEST=None):
        """ """
        user_ob = self.getUser(name)
        email = email.strip()
        if password == '' and confirm == '':
            password = confirm = None
        if not firstname:
            raise ValidationError, 'The first name must be specified'
        if not lastname:
            raise ValidationError, 'The last name must be specified'
        if not email:
            raise ValidationError, 'The email must be specified'
        if not is_valid_email(email):
            raise ValidationError, 'Invalid email address.'

        #If the e-mail address changed check if it's not used
        if user_ob.email != email.strip():
            users = self.getUserNames()
            for n in users:
                us = self.getUser(n)
                if email == us.email:
                    raise i18n_exception(ValidationError,
                        'A user with the specified email already exists, '
                        'username ${user}', user=n)
        if not name:
            raise ValidationError, 'A username must be specified'
        if not self.getUser(name):
            raise ValidationError, 'Unknown user'
        if (password or confirm) and (password != confirm):
            raise ValidationError, 'Password and confirmation do not match'

        #convert data
        roles = self.getUserRoles(user_ob)
        domains = user_ob.getDomains()
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(name, password, roles, domains, firstname, lastname,
                           email, lastupdated)
        if REQUEST is not None: REQUEST.RESPONSE.redirect('manage_users_html')

    security.declareProtected(manage_users, 'manage_addUsersRoles')
    def manage_addUsersRoles(self, name='', roles=[], location='',
                             REQUEST=None):
        """ """
        roles = self.utConvertToList(roles)

        if not name:
            raise ValidationError('A username must be specified')
        if not roles:
            raise ValidationError('No roles were specified')
        if location == '' or location == '/':
            self._doChangeUserRoles(name, roles)
        else:
            location_obj = self.getSite().unrestrictedTraverse(location, None)
            if location_obj is None:
                raise ValidationError('Invalid location')
            location_obj.manage_setLocalRoles(name, roles)

        if REQUEST: REQUEST.RESPONSE.redirect('manage_userRoles_html')

    security.declareProtected(manage_users, 'manage_revokeUserRole')
    def manage_revokeUserRole(self, user, location, REQUEST=None):
        """ """
        user = [user]
        if location == '' or location == '/':
            self._doDelUserRoles(user)
        else:
            location_obj = self.utGetObject(location)
            location_obj.manage_delLocalRoles(user)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_userRoles_html')

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
        return sorted(self.data.keys())

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
        for folder in self.getCatalogedObjects(
                meta_type=[METATYPE_FOLDER,'Folder'],
                has_local_role=1, path=path):
            for roles_tuple in folder.get_local_roles():
                local_roles = self.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] in self.user_names() and len(local_roles) > 0:
                    if not users_roles.has_key(str(roles_tuple[0])):
                        users_roles[str(roles_tuple[0])] = []
                    users_roles[str(roles_tuple[0])].append(
                            (local_roles, folder.absolute_url(1)))
        return users_roles

    security.declareProtected(manage_users, 'getUsersRolesRestricted')
    def getLocationUserRoles(self, user_id, path):
        """
        Returns information about the user's local roles at the exact location.
        If location is site, returns roles in site.

        Basically the same as Zope's location.get_local_roles_for_userid,
        but works for any type of user (local, from source)
        in any type of location (portal root, folder)

        """
        user = self.get_user_with_userid(user_id)
        roles = set()
        if path in ("/", ""):
            roles.update(set(self.getUserRoles(user)))

        # when user is not local, also has the roles here for site obj
        folder = self.getSite().unrestrictedTraverse(path, None)
        if folder:
            for roles_tuple in folder.get_local_roles():
                local_roles = self.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] == user_id and len(local_roles) > 0:
                    roles.update(set(local_roles))

        return list(roles - set(['Owner', 'Anonymous', 'Authenticated']))

    security.declareProtected(manage_users, 'search_users')
    def search_users(self, query, REQUEST=None, **kw):
        """ Search users based of query and other criteria, returning user
        like objects or rendered html for an ajax request.

        Arguments:

        all_users -- default False (local users only),
                     True - to get users from all sources
        """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = kw

        all_users = bool(form_data.get('all_users', False))
        skey = form_data.get('skey', 'name')
        rkey = int(form_data.get('rkey', 0))
        filter_role = form_data.get('role', '')
        filter_location = form_data.get('location', '_all_')

        assert isinstance(query, basestring)
        query = query.strip()
        query = self.utToUtf8(query).lower()

        # gather basic information for users
        users_info = self.get_users_info(not all_users)

        # filter users by query
        def match_user(user_info):
            if not user_info:
                return None
            return (user_info.user_id.lower().find(query) !=-1 or
                    user_info.full_name.lower().find(query) !=-1 or
                    user_info.email.lower().find(query) !=-1)
        users_info = filter(match_user, users_info)

        # gather source title for remaining users
        for user_info in users_info:
            if user_info._source == self:
                user_info.source_title = u'Local'
            else:
                user_info.source_title = force_to_unicode(
                                                    user_info._source.title)
        # sort users by skey
        def sort_key(obj):
            if skey == 'username':
                return force_to_unicode(obj.user_id).lower()
            elif skey == 'source':
                return force_to_unicode(obj.source_title).lower()
            elif skey == 'email':
                return force_to_unicode(obj.email).lower()
            else:
                return force_to_unicode(obj.full_name).lower()
        users_info.sort(key=sort_key, reverse=bool(rkey))

        # filter by role and location
        if filter_role == 'noroles':
            #users_roles = {userid: [([role, ...], location), ...], ...}
            users_roles = self.get_all_users_roles()
            users_info = [user_info for user_info in users_info
                                        if user_info.user_id not in users_roles]
        else:
            #users_roles = {userid: [([role, ...], location), ...], ...}
            if filter_location == '_all_':
                users_roles = self.get_all_users_roles()
            else:
                users_roles = self.get_all_users_roles(filter_location)

            if filter_role:
                # remove all roles not equal to filter_role
                filtered_users_roles = {}
                for user_id in users_roles:
                    for roles, location in users_roles[user_id]:
                        if filter_role in roles:
                            filtered_users_roles.setdefault(user_id, [])
                            filtered_users_roles[user_id].append(
                                                    ([filter_role], location))
                users_roles = filtered_users_roles

            if filter_role != '' or filter_location != '_all_':
                users_info = [user_info for user_info in users_info
                                            if user_info.user_id in users_roles]

        # gather role info
        for user_info in users_info:
            user_info.roles = users_roles.get(user_info.user_id, [])

        # gather is new user info
        for user_info in users_info:
            try:
                user_info.is_new_user = self.isNewUser(user_info.zope_user)
            except AttributeError: # should work for local users only
                user_info.is_new_user = False

        disabled_type = form_data.get('disabled_type', 'no_disabled')
        # sort according to disabled_type
        response = []
        for usr in users_info:
            mail = getattr(usr, 'email', '')
            status_disabled = getattr(usr, 'status', 'active') == 'disabled'
            is_disabled = (DISABLED_EMAIL in mail) or status_disabled
            if ((disabled_type == 'no_disabled') and (not is_disabled)
                or
                (disabled_type == 'include_disabled')
                or
                ((disabled_type == 'only_disabled') and is_disabled)
                ):
                response.append(usr)
        return response

    def revoke_searched_roles(self, usernames, role_to_revoke, filter_location,
                              REQUEST=None):
        """ """
        if REQUEST:
            # for logging
            manager_id = REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            manager_id = None
        # get current roles + filter location
        if filter_location == '_all_':
            users_roles = self.get_all_users_roles()
        else:
            users_roles = self.get_all_users_roles(filter_location)

        for user_id in usernames:
            for local_roles, location in users_roles.get(user_id, []):
                if role_to_revoke: # keep the other roles the user has
                    if role_to_revoke not in local_roles:
                        continue
                    all_roles = location.get_local_roles_for_userid(user_id)
                    roles_to_set = list(set(all_roles) - set([role_to_revoke]))
                    if roles_to_set:
                        location.manage_setLocalRoles(user_id, roles_to_set)
                    else:
                        location.manage_delLocalRoles([user_id])
                    actually_revoked = [role_to_revoke]
                else: # remove all roles
                    actually_revoked = location.get_local_roles_for_userid(user_id)
                    location.manage_delLocalRoles([user_id])
                if manager_id:
                    notify(RoleAssignmentEvent(location, manager_id,
                               user_id, [], actually_revoked,
                               send_mail='Administrator' in actually_revoked))

        # remove local roles for the site
        if filter_location in ['_all_', '']: # remove site roles
            for user_id in usernames:
                if user_id not in self.user_names():
                    continue
                local_user = self.getUser(user_id)
                if role_to_revoke: # keep the other roles the user has
                    if role_to_revoke not in local_user.roles:
                        continue
                    local_user.roles.remove(role_to_revoke)
                    actually_revoked = [role_to_revoke]
                else: # remove all roles
                    actually_revoked = local_user.roles
                    local_user.roles = []
                if manager_id:
                    notify(RoleAssignmentEvent(self.getSite(), manager_id,
                               user_id, [], actually_revoked,
                               send_mail='Administrator' in actually_revoked))


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
                if (user.name.find(self.utToUtf8(query))!=-1 or
                    user.email.find(self.utToUtf8(query))!=-1 or
                    user.firstname.find(self.utToUtf8(query))!=-1 or
                    user.lastname.find(self.utToUtf8(query))!=-1
                ):
                    users_a((user.name, '%s %s' % (
                        user.firstname, user.lastname), user.email))
            if limit and len(users) > int(limit):
                return 0, []
            else:
                return 1, users
        else:
            return 2, []

    def get_zope_env(self, key):
        return get_zope_env(key)

    security.declareProtected(manage_users, 'get_local_usernames')
    def get_local_usernames(self):
        local_users = self.user_names()
        ret = [{'name': self.getUserFullName(self.getUser(user_id)),
                'uid': user_id,
                'is_new_user': self.isNewUser(self.getUser(user_id))}
                    for user_id in local_users]
        user_list = sorted(ret, key=lambda user: user['name'].lower())
        #Move new users to the top if we are not in EEA (=no external sources)
        old_users = list(user_list)
        new_users = []
        if not get_zope_env('NETWORK_NAME').lower() == 'eionet':
            for user in user_list:
                if user['is_new_user']:
                    new_users.append(old_users.pop(old_users.index(user)))
        return new_users + old_users

    security.declareProtected(manage_users, 'isNewUser')
    def isNewUser(self, user_obj, days=5):
        """
        return True if user was created in the last 5 days
        note: the `days` parameter is not used.
        """
        return (DateTime() - DateTime(self.getUserCreatedDate(user_obj))) <= 5

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
        names_sorted = sorted(self.data.keys())
        return [self.data[name] for name in names_sorted]

    security.declareProtected(view, 'getUser')
    def getUser(self, name):
        """
        Return the user object for the specified userid ( None if not found)
        """
        return self.data.get(name, None)

    def getAuthenticatedUserRoles(self, p_meta_types=None):
        """
        Returns a list with all roles of the authenticated user.
        """
        user = self.REQUEST.AUTHENTICATED_USER
        return self.getUserLocalRoles(user, p_meta_types)

    def getUserLocalRoles(self, user, p_meta_types=None, try_groups=True):
        """
        Return list of local roles for a specified user

        This function looks at the site level, then inside all folders for
        local roles.
        """
        if p_meta_types is None: p_meta_types = self.get_containers_metatypes()
        r = []
        ra = r.append
        username = user.getUserName()
        userroles = self.utConvertToList(self.getUserRoles(user))
        for x in ['Anonymous', 'Authenticated', 'Owner']:
            if x in userroles:
                userroles.remove(x)
        if len(userroles): ra((userroles, ''))
        folders = self.getCatalogedObjects(meta_type=p_meta_types,
                    has_local_role=1)
        folders.insert(0, self.getSite())
        for folder in folders:
            for roles_tuple in folder.get_local_roles():
                local_roles = self.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] == username and len(local_roles) > 0:
                    ra((local_roles, folder.absolute_url(1)))

        if try_groups:
            for source in self.getSources():
                if not hasattr(source, 'get_groups_roles_map'):
                    continue
                for group, roles in source.get_groups_roles_map().iteritems():
                    if source.user_in_group(user, group):
                        r_dict = {}
                        for role in roles:
                            r_dict.setdefault(role[1]['path'], [])
                            r_dict[role[1]['path']].append(role[0])
                        for path, roles in r_dict.iteritems():
                            ra((roles, path))

        return r

    def isAdministrator(self, path=''):
        """
        Check if the current user has Administrator role at the specified
        path (by default, at the site level)
        """
        list_roles = self.getAuthenticatedUserRoles()
        for roles, path in list_roles:
            if ((('Manager' in roles) or ('Administrator' in roles)) and
                    path == ''):
                return True
            elif ((('Manager' in roles) or ('Administrator' in roles)) and
                    path == path):
                return True
        return False

    def getUsersRoles(self, meta_types=None):
        """
        Same as getAuthenticatedUserRoles, except for all the users registered
        in this folder.

        Output format: a dict with keys=userids and values=list of roles. The
        list of roles contains tuples of (list of role names, path of folder).
        """
        current_site = self.getSite()
        sites = [current_site]
        # search for any sub-sites directly below current_site
        for child in current_site.objectValues():
            if INySite.providedBy(child):
                sites.append(child)

        users_roles = {}
        for username in self.user_names():   #get the users
            user = self.getUser(username)
            users_roles[username] = [(self.getUserRoles(user), '')]

        for site in sites:
            if meta_types is None:
                picked_meta_types = site.get_containers_metatypes()
            else:
                picked_meta_types = meta_types

            for folder in site.getCatalogedObjects(meta_type=picked_meta_types,
                    has_local_role=1):
                for roles_tuple in folder.get_local_roles():
                    local_roles = self.getLocalRoles(roles_tuple[1])
                    if roles_tuple[0] in self.user_names() and len(local_roles) > 0:
                        roles_list = users_roles[str(roles_tuple[0])]
                        roles_list.append((local_roles,
                                    relative_object_path(folder, current_site)))
        return users_roles

    security.declareProtected(manage_users, 'getUsersWithRoles')
    def getUsersWithRoles(self):
        """
        Honestly, we're stumped. Don't use this in new code.
        """
        users = {}
        for k, v in self.getUsersRoles().items():
            if ((len(v) > 1 and len(v[1][0]) > 0) or
                (len(v) == 1 and len(v[0][0]) > 0)):
                users[k] = v
        return users

    security.declareProtected(manage_users, 'getUsersWithRole')
    def getUsersWithRole(self, roles=[]):
        """
        Don't use this in new code.
        return the user objects that have the specified role
        """
        if not isinstance(roles, list):
            roles = [roles]
        def handle_unicode(s):
            if not isinstance(s, unicode):
                try:
                    return s.decode('utf-8')
                except:
                    return s.decode('latin-1')
            else:
                return s
        local_users = self.getUsersWithRoles()
        #dictionary that will hold local users
        local_result = {}
        for user_id, user_roles in local_users.items():
            for location in user_roles:
                if set(location[0]).intersection(set(roles)):
                    if user_id not in local_result.keys():
                        user_obj = self.getUser(user_id)
                        user_name = "%s %s" % (self.getUserFirstName(user_obj),
                                self.getUserLastName(user_obj))
                        user_email = self.getUserEmail(user_obj)
                        local_result[user_id] = {
                            'name': handle_unicode(user_name),
                            'email': user_email
                        }


        #dictionary that will hold external users
        external_users = {}
        for source in self.getSources():
            #acl_folder = source.getUserFolder()
            source_obj = self.getSourceObj(source.getId())
            users = source_obj.getSortedUserRoles(skey='user')
            for user in users:
                user_roles = user[3]
                for user_role in user_roles:
                    if set(user_role[0]).intersection(set(roles)):
                        user_id = user[0]
                        user_name = user[1]
                        user_email = source_obj.getUserEmail(user_id,
                                source_obj.getUserFolder())
                        external_users[user_id] = {
                            'name': handle_unicode(user_name),
                            'email': user_email
                        }
            if not hasattr(source, 'get_groups_roles_map'):
                continue
            group_users = {}
            for group, group_roles in source.get_groups_roles_map().items():
                if not set(roles).intersection([x[0] for x in group_roles]):
                    continue
                userids = source.group_member_ids(group)
                for userid in userids:
                    user_info = source.get_source_user_info(userid)
                    group_users[userid] = {
                        'name': handle_unicode(user_info.full_name),
                        'email': handle_unicode(user_info.email),
                    }
            #update external users
            external_users.update(group_users)

        #add external users data to local_result
        local_result.update(external_users)
        #and return everything
        return local_result

    def getSortedUsersWithRoles(self, roles, skey, rkey):
        result = []
        for userid, userdata in self.getUsersWithRole(roles).items():
            to_append = userdata
            to_append['uid'] = userid
            result.append(to_append)
        return self.utSortDictsListByKey(result, skey, rkey)

    def getUserSource(self, user):
        """
        Returns information about where a user is registered:
         - if it's inside this user folder, return 'acl_users'
         - if it's in a known external source, returns the source's title
         - otherwise returns 'n/a'
        """

        if not isinstance(user, basestring):
            warn("Passign user objects to `getUserSource` is highly suspect.")
            user = str(user)

        user_ob = self.getUser(user)
        if user_ob:
            return 'acl_users'
        else:
            for source in self.getSources():
                # here we convert `user` to `str` because, for some strange
                # reason, some user IDs are stored as `unicode` in the DB
                if source.has_user(str(user)):
                    return source.title
            else:
                return 'n/a'

    security.declarePrivate('get_local_user_info')
    def get_local_user_info(self, user_id):
        zope_user = self.getUser(user_id)

        fields = {
            'user_id': str(zope_user.getId()),
            'email': force_to_unicode(zope_user.email),
            'first_name': force_to_unicode(zope_user.firstname),
            'last_name': force_to_unicode(zope_user.lastname),
            '_get_zope_user': lambda: zope_user,
            '_source': self,
        }
        fields['full_name'] = u'%s %s' % (fields['first_name'],
                                          fields['last_name'])
        return LocalUserInfo(**fields)

    security.declarePrivate('get_user_info')
    def get_user_info(self, user_id):
        """
        Given a `user_id`, search for the user locally and in all sources
        (plugins). If the user is found, `get_user_info` returns a
        UserInfo object, otherwise it raises `KeyError`.
        """
        if self.getUser(user_id):
            return self.get_local_user_info(user_id)
        else:
            for source in self.getSources():
                if source.has_user(user_id):
                    return source.get_source_user_info(user_id)
            else:
                raise KeyError("User not found: %r" % (user_id,))

    security.declarePrivate('get_users_info')
    def get_users_info(self, local_users_only=False):
        """
        Returns the user info for all local users and all users in the sources.
        For LDAP sources only returns the users that have roles in the site.
        """
        user_info_objects = [self.get_user_info(username)
                                for username in self.getUserNames()]
        if local_users_only:
            return user_info_objects

        for user_source in self.getSources():
            user_folder = user_source.getUserFolder()
            if user_folder.meta_type == 'User Folder':
                user_info_objects.extend([self.get_user_info(username)
                    for username in user_folder.getUserNames()])
            elif user_folder.meta_type == 'LDAPUserFolder':
                user_info_objects.extend([self.get_user_info(username)
                    for username in user_source.getUsersRoles(user_folder)])
        return user_info_objects

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
            user_folder = source.getUserFolder()
            user = user_folder.getUser(userid)
            if user is not None:
                return user.__of__(user_folder)

        return None

    security.declarePublic('name_from_userid')
    def name_from_userid(self, userid):
        """
        Given a userid, try to get its full name. If userid is None then we
        assume it's an anonymous user, and return `"Anonymous User"`. If we
        can't find the user, return an empty string.

        This function returns `unicode` objects, unlike the rest of
        Naaya's user code, that prefers utf8-encoded strings.
        """
        if userid is None:
            return u"Anonymous User"

        if userid in self.user_names():
            user_ob = self.getUser(userid)
            return force_to_unicode(self.getUserFullName(user_ob))

        for source in self.getSources():
            source_acl = source.getUserFolder()
            name = source.getUserFullName(userid, source_acl)
            if name is not None:
                return force_to_unicode(name)

        return u''

    security.declarePublic('source_name_from_userid')
    def source_name_from_userid(self, userid):
        """
        Given a userid, return the source name (local, EIONET, or...)
        """
        if userid is None:
            return u''

        if userid in self.user_names():
            return 'Local'

        for source in self.getSources():
            source_acl = source.getUserFolder()
            name = source.getUserFullName(userid, source_acl)
            if name is not None:
                return getattr(source, 'title', u'')

        return u''

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

    security.declarePrivate('lookup_user_by_email')
    def lookup_user_by_email(self, email):
        for user in self.getUsers():
            if user.email.lower() == email.lower():
                yield user

    security.declarePublic('get_user_photo_url')
    def get_user_photo_url(self, user_id=None):
        """
        Get the user photo URL for the user_id. Returns the URL for the
        logged-in user if no user_id specified.

        Checks for administrator permission for getting other users photos.
        """
        if user_id is None:
            cuser_id = self.get_current_userid()
        else:
            cuser_id = user_id

        try:
            user_info = self.get_user_info(cuser_id)
        except KeyError, ke:
            log.warn(str(ke))
            return

        if hasattr(user_info, 'jpegPhoto') and user_info.jpegPhoto:
            if user_id is None:
                return self.absolute_url() + '/user_photo'
            else:
                return self.absolute_url() + '/user_photo?user_id=' + user_id

    security.declarePublic('user_photo')
    def user_photo(self, REQUEST, RESPONSE, user_id=None):
        """
        Get the user photo for the user_id. Returns the photo for the
        logged-in user if no user_id specified.

        Checks for administrator permission for getting other users photos.
        """
        if user_id is None:
            user_id = self.get_current_userid()

        try:
            user_info = self.get_user_info(user_id)
        except KeyError, ke:
            log.warn(str(ke))
            return

        if hasattr(user_info, 'jpegPhoto') and user_info.jpegPhoto:
            RESPONSE.setHeader('Content-Type', 'image/jpeg')
            return user_info.jpegPhoto

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
    def get_all_user_roles(self, user):
        """
        Given a userid, returns all the roles of that user, looking at this
        user folder and any external sources.
        """
        uid = user.getUserName()
        # check local users
        roles = []
        local_user = self.getUser(uid)
        if local_user is not None:
            return local_user.roles
        # check ldap users and groups
        for source in self.getSources():
            # users
            portal_roles = source.getUsersRoles(
                    source.getUserFolder()).get(uid, [])
            if portal_roles:
                for role, location in portal_roles:
                    if location == self.getSite().absolute_url(1):
                        roles.extend(role)
            # groups
            try:
                roles.extend(source.get_group_roles_in_site(user))
            except AttributeError:
                pass # probably not an LDAP plugin

        roles.extend(user.getRoles())
        return roles

    def get_all_users_roles(self, filter_path=''):
        """
        Returns a structure with user roles by objects starting from filter_path
        {userid: [([role, ...], location), ...], ...}
        """
        users_roles = {}
        this_site = self.getSite()
        # site roles for local users
        if filter_path == '':
            for username in self.user_names():
                local_user = self.getUser(username)
                if local_user.roles:
                    users_roles[username] = [(local_user.roles, this_site)]

        # search for sub-sites directly below the current site
        sites = [self.getSite()] + [obj for obj in self.getSite().objectValues()
                                            if INySite.providedBy(obj)]
        for site in sites:
            path = relative_object_path(site, this_site)
            if (not path.startswith(filter_path)
                    and not filter_path.startswith(path)):
                continue

            containers = site.getCatalogedObjects(
                            meta_type=site.get_containers_metatypes(),
                            has_local_role=1)
            containers.append(site)
            for container in containers:
                path = relative_object_path(container, this_site)
                if not path.startswith(filter_path):
                    continue

                for roles_tuple in container.get_local_roles():
                    user = roles_tuple[0]
                    username = str(user)
                    local_roles = self.getLocalRoles(roles_tuple[1])
                    if local_roles:
                        users_roles.setdefault(username, []).append(
                                (local_roles, container))
        return users_roles

    security.declareProtected(manage_users, 'get_all_containers_with_roles')
    def get_all_containers_with_roles(self):
        """
        Returns a list of objects with user roles
        all sites are included by default
        """
        ret = []

        sites = [self.getSite()] + [obj for obj in self.getSite().objectValues()
                                            if INySite.providedBy(obj)]
        for site in sites:
            site_containers = []
            containers = site.getCatalogedObjects(
                            meta_type=site.get_containers_metatypes(),
                            has_local_role=1)
            for container in containers:
                for roles_tuple in container.get_local_roles():
                    local_roles = self.getLocalRoles(roles_tuple[1])
                    if local_roles:
                        site_containers.append(container)
                        break
            site_containers.sort(key=lambda x: x.title_or_id())
            site_containers = [site] + site_containers
            ret.append(site_containers)
        return ret

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
        if user_obj.getUserName() == 'Anonymous User':
            return 'Anonymous User'
        try:
            return u'%s %s' % (force_to_unicode(user_obj.firstname),
                               force_to_unicode(user_obj.lastname))
        except AttributeError:
            return u''

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

    #security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSources')
    def getSources(self):
        """
        returns a list with all registered external sources
        """
        return map(self._getOb, map(lambda x: x['id'], self._objects))

    #security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSourceObj')
    def getSourceObj(self, p_source_id):
        """
        returns a source object
        """
        try: return self._getOb(p_source_id)
        except: return None

    def manageAddSource(self, source_path, title='', REQUEST = None):
        """ """
        source_obj = self.unrestrictedTraverse('/' + source_path, None)
        plugin_factory = self.getPluginFactory(source_obj.meta_type)

        id = self.utGenRandomId()
        plugin_obj = plugin_factory(id, source_obj, title)
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

    def makeRolesString(self, roles, path='', date=None,
            user_granting_roles=None, from_group=None):
        filtered_roles = self.getLocalRoles(roles)
        if filtered_roles == []:
            return None

        if path == '':
            path = 'entire site'

        ret = '%s on %s' % (', '.join(filtered_roles), path)

        if date is not None and user_granting_roles is not None:
            ret += ' granted on %s by %s' % (date, user_granting_roles)

        if from_group is not None:
            ret += ' from group %s' % from_group

        return ret


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
        csv_writer.writerow(['Username', 'Name', 'Organisation',
                             'Postal address', 'Email address',
                             'LDAP Group(s)', 'Roles', 'Account type'])

        # get local_roles_by_location[location][user] = list of {roles, date, user_granting_roles}
        local_roles_by_location = {}
        meta_types = ['Naaya Folder', 'Naaya Photo Gallery', 'Naaya Photo Folder',
                'Naaya Forum', 'Naaya Forum Topic', 'Naaya TalkBack Consultation',
                'Naaya Survey Questionnaire']
        locations = self.getCatalogedObjects(meta_type=meta_types, has_local_role=1)
        locations.append(self.getSite())
        for l in locations:
            local_roles_by_location[l.absolute_url(1)] = IRoleLogger(l).getAllLocalRolesInfo()

        # get user_roles[user] = list of {roles, date, user_granting_roles}
        user_roles = IRoleLogger(self.getSite()).getAllUserRolesInfo()

        # local_roles_by_location[location][user] -> roles_by_user[user][location]
        roles_by_user = {}
        for l, v in local_roles_by_location.items():
            for u, data in v.items():
                if not roles_by_user.has_key(u):
                    roles_by_user[u] = {}
                roles_by_user[u][l] = data

        # user_roles[user] -> roles_by_user[user][location]
        for u, data in user_roles.items():
            if not roles_by_user.has_key(u):
                roles_by_user[u] = {}
            roles_by_user[u][self.getSite().absolute_url(1)] = data


        # get group_roles_by_location[location][group] = list of {roles, date, user_granting_roles}
        group_roles_by_location = {}
        locations = self.getCatalogedObjects(meta_type=meta_types)
        locations.append(self.getSite())
        for l in locations:
            group_roles_by_location[l.absolute_url(1)] = IRoleLogger(l).getAllLDAPGroupRolesInfo()

        # group_roles_by_location[location][group] -> group_roles_by_group[group][location]
        group_roles_by_group = {}
        for l, v in group_roles_by_location.items():
            for g, data in v.items():
                if not group_roles_by_group.has_key(g):
                    group_roles_by_group[g] = {}
                group_roles_by_group[g][l] = data

        # get groups_data[group] = {source, members}
        groups_data = {}
        for group in group_roles_by_group.keys():
            for source in self.getSources():
                userids = source.group_member_ids(group)
                if userids != []:
                    groups_data[group] = {
                            'source': source,
                            'members': userids
                            }
                    break

        # get groups_for_user[userid] = list of groups
        groups_for_user = {}
        for group, v in groups_data.items():
            for userid in v['members']:
                if userid not in groups_for_user:
                    groups_for_user[userid] = []
                groups_for_user[userid].append(group)

        # all_users
        all_users = []
        all_users.extend(roles_by_user.keys())
        all_users.extend(groups_for_user.keys())
        all_users = list(set(all_users))

        for userid in all_users:
            groups = groups_for_user.get(userid, [])

            roles_for_user = roles_by_user.get(userid, {})

            try:
                user_info = self.get_user_info(userid)
            except KeyError:
                # user not found. skip it.
                continue
            name = user_info.full_name
            organisation = getattr(user_info, 'organisation', u"")
            postal_address = getattr(user_info, 'postal_address', u"")
            email = user_info.email
            source = user_info._source

            if source == self:
                user_type = 'Local'
                groups_str = ''

            else:
                user_type = 'LDAP (source_id=%s)' % source.id
                if groups == []:
                    groups_str = source.getUserLocation(userid)
                else:
                    groups_str = ', '.join(groups)

            roles_info_str_list = []
            for path, roles_infos in roles_for_user.items():
                for ri in roles_infos:
                    roles_info_str = self.makeRolesString(
                            ri['roles'],
                            path,
                            ri.get('date', None),
                            ri.get('user_granting_roles', None))
                    if roles_info_str is not None:
                        roles_info_str_list.append(roles_info_str)
            # add roles from groups
            for g in groups:
                for path, roles_infos in group_roles_by_group[g].items():
                    for ri in roles_infos:
                        roles_info_str = self.makeRolesString(
                                ri['roles'],
                                path,
                                ri.get('date', None),
                                ri.get('user_granting_roles', None),
                                g)
                        if roles_info_str is not None:
                            roles_info_str_list.append(roles_info_str)

            roles_str = ' | '.join(roles_info_str_list)

            csv_writer.writerow([
                self.utToUtf8(userid),
                self.utToUtf8(name),
                self.utToUtf8(organisation),
                self.utToUtf8(postal_address),
                self.utToUtf8(email),
                self.utToUtf8(groups_str),
                roles_str,
                user_type,
            ])

        RESPONSE.setHeader('Content-Type', 'text/x-csv')
        RESPONSE.setHeader('Content-Length', output.len)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="users.csv"')

        ret = output.getvalue()

        return ret

    security.declareProtected(manage_users, 'get_send_emails_log_items')
    def get_send_emails_log_items(self):
        """
        Returns all email errors

        E.g. send email errors are logged on group roles changing.
        This is done in a separate thread.
        Errors are appended to '_send_emails_log' attribute.
        """
        return getattr(self, '_send_emails_log', PersistentList())[::-1]

    security.declareProtected(manage_users, 'clear_send_emails_log')
    def clear_send_emails_log(self, REQUEST=None):
        """
        Clear all email errors

        E.g. send email errors are logged on group roles changing.
        This is done in a separate thread.
        Errors are appended to '_send_emails_log' attribute.
        """
        self._send_emails_log = PersistentList()

        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_send_emails_log_html')

    security.declareProtected(manage_users, 'manage_importUsers')
    def manage_importUsers(self, data=None, REQUEST=None):
        """ """

        #import_errors = {}
        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        errors = []

        try:
            reader = UnicodeReader(data)
            try:
                header = reader.next()
            except StopIteration:
                msg = 'Invalid CSV file'
                if REQUEST is None:
                    raise ValueError(msg)
                else:
                    errors.append(msg)
                    reader = []

            record_number = 0
            successfully_imported = 0

            space_pattern = r'\s+'
            for row in reader:
                try:
                    record_number += 1
                    properties = {}
                    record_errors = []
                    for column, value in zip(header, row):
                        if column == 'roles':
                            if not properties.has_key('roles'):
                                properties['roles'] = []
                            if value:
                                properties['roles'].append(value.strip())
                        else:
                            properties[column] = value.strip()
                    email = properties.get('email')
                    name = properties.get('name')
                    firstname = properties.get('firstname')
                    lastname = properties.get('lastname')
                    password = properties.get('password')
                    roles = properties.get('roles')
                    domains = properties.get('domains')

                    name = str(name).lower()
                    name = re.sub(space_pattern, '.', name)
                    firstname = firstname.capitalize()
                    lastname = lastname.capitalize()
                    email = str(email).lower()

                    if not check_username(name):
                        record_errors.append('Record %s: Username: only letters, numbers, dot (.), minus (-) and underscore (_) are allowed' % record_number)
                    if not firstname:
                        record_errors.append('Record %s: The first name must be specified' % record_number)
                    if not lastname:
                        record_errors.append('Record %s: The last name must be specified' % record_number)
                    if not email:
                        record_errors.append('Record %s: The email must be specified' % record_number)
                    if not is_valid_email(email):
                        record_errors.append('Record %s: Invalid email address.' % record_number)
                    if not name:
                        record_errors.append('Record %s: A username must be specified' % record_number)
                    if not password:
                        record_errors.append('Record %s: Password must be specified' % record_number)

                    existing_usernames = set(username.lower for username in self.getUserNames())
                    if self.get_user_with_userid(name) is not None or name in existing_usernames:
                        record_errors.append('Record %s: Username %s already in use' % (record_number, name))

                    existing_emails = set(user.email.lower() for user in self.getUsers())
                    if email in existing_emails:
                        users_with_same_email = [user.name for user in self.getUsers()
                            if user.email.lower() == email]
                        record_errors.append('Record %s: Email %s already in use - user(s): %s'
                            % (record_number, email, ', '.join(users_with_same_email)))
                    if record_errors:
                        errors += record_errors
                        continue

                    user = self._doAddUser(name, password, roles, domains, firstname, lastname, email)
                    successfully_imported += 1

                except UnicodeDecodeError, e:
                    raise
                except Exception, e:
                    self.log_current_error()
                    msg = ('Error while importing from CSV, row ${record_number}: ${error}',
                           {'record_number': record_number, 'error': str(e)})
                    if REQUEST is None:
                        raise ValueError(msg)
                    else:
                        errors.append(msg)

        except UnicodeDecodeError, e:
            if REQUEST is None:
                raise
            else:
                errors.append('CSV file is not utf-8 encoded')
        if errors:
            self.setSessionErrorsTrans(errors)
        if REQUEST is not None:
            if successfully_imported > 0:
                self.setSessionInfoTrans('%s user(s) successfully imported.' % successfully_imported)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(manage_users, 'template')
    def template(self, as_attachment=True, REQUEST=None):
        """ """
        output = StringIO()
        columns = ['firstname', 'lastname','email', 'name', 'password', 'roles', 'domains']
        csv.writer(output).writerow(columns)
        if as_attachment and REQUEST is not None:
            filename = 'users import.csv'
            set_response_attachment(REQUEST.RESPONSE, filename,
                'text/csv; charset=utf-8', output.len)
        return output.getvalue()

    security.declareProtected(view, 'get_ldap_user_groups')
    def get_ldap_user_groups(self, user_id):
        """ """
        try:
            from eea.usersdb.factories import agent_from_site
        except ImportError:
            return []
        agent = agent_from_site(self)
        ldap_roles = sorted(agent.member_roles_info('user',
                                                    user_id,
                                                    ('description',)))

        return ldap_roles

    manage_users_html = PageTemplateFile('zpt/authentication_content', globals())
    manage_addUser_html = PageTemplateFile('zpt/authentication_adduser', globals())
    manage_editUser_html = PageTemplateFile('zpt/authentication_edituser', globals())

    manage_userRoles_html = PageTemplateFile('zpt/authentication_user_roles', globals())
    sitemap = PageTemplateFile('zpt/authentication_sitemap', globals())

    manage_sources_html = PageTemplateFile('zpt/authentication_sources', globals())
    manage_source_html = PageTemplateFile('zpt/authentication_source', globals())

    manage_send_emails_log_html = PageTemplateFile('zpt/authentication_send_emails_log', globals())

    recover_password = RecoverPassword('recover_password')

InitializeClass(AuthenticationTool)
