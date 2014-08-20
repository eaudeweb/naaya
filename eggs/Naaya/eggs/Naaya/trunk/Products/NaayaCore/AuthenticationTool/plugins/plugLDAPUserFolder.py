import logging

import Acquisition
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from AccessControl.unauthorized import Unauthorized
from Globals import InitializeClass
from Missing import MV
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from persistent.dict import PersistentDict
from zope.event import notify
from zope.interface import implements

try:
    import ldap
    #from Products.LDAPUserFolder.utils import GROUP_MEMBER_MAP
    from Products.LDAPUserFolder.LDAPDelegate import filter_format
except:
    pass

from Products.NaayaCore.AuthenticationTool.plugBase import PlugBase
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import UserInfo
from Products.NaayaCore.AuthenticationTool.events import RoleAssignmentEvent
from Products.NaayaCore.AuthenticationTool.interfaces import IAuthenticationToolPlugin

from Products.Naaya.NySite import NySite
from Products.NaayaBase.events import NyAddGroupRoleEvent, NyRemoveGroupRoleEvent

from naaya.core.utils import is_ajax
from naaya.core.zope2util import relative_object_path
import naaya.cache.cache as naaya_cache

import ldap_cache

LDAP_ROOT_ID = 'ROOT'

log = logging.getLogger('naaya.core.auth.ldap')

class LDAPUserNotFound(Exception):
    pass

class ldap_user:
    """Defines a ldap_user. """

    def __init__(self, id, dn, cn, description, parent, childs, cached):
        """Constructor"""
        self.id = id    #unique id, integer
        self.dn = dn    #cannonical name, string
        self.cn= cn     #distinguished name, string
        self.description = description  #string
        self.parent = parent    #parent's id, integer
        self.childs = childs    #a list with all childs nodes
        self.cached = cached    #if this node content is chached or not

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ldap_user)

class plugLDAPUserFolder(PlugBase):
    """ Plugin for LDAPUserFolder """

    implements(IAuthenticationToolPlugin)

    object_type = 'LDAPUserFolder'
    meta_type = 'Plugin for user folder'
    group_to_roles_mapping = PersistentDict()

    @property
    def default_encoding(self):
        try:
            from Products.LDAPUserFolder.utils import encoding
        except Exception:
            return 'utf-8'
        else:
            return encoding

    def __init__(self, id, source_obj, title):
        """ constructor """
        super(plugLDAPUserFolder, self).__init__(id, source_obj, title)
        self._user_objs = {}
        self.located = {}
        self.buffer = {}

    security = ClassSecurityInfo()

    def getUserLocation(self, user):
        return self.located.get(user, '-')

    def setUserLocation(self, user, user_location):
        self.located[user] = user_location
        self._p_changed = 1

    def delUserLocation(self, user):
        try:
            del self.located[user]
            self._p_changed = 1
        except:
            pass

    def sort_list(self, list, n, r):
        #returns a sorted list of messages - sort without case-sensitivity
        t = [(x[n].lower(), x) for x in list]
        t.sort()
        if r: t.reverse()
        return [val for (key, val) in t]

    def initializeCache(self, root_dn):
        """Init"""
        self._user_objs[LDAP_ROOT_ID] = ldap_user(LDAP_ROOT_ID, root_dn, LDAP_ROOT_ID, LDAP_ROOT_ID, '', [], 0)
        self._p_changed = 1

    def deleteCache(self, acl_folder):
        """Delete cache"""
        self.initializeCache(self.getRootDN(acl_folder))
        self._p_changed = 1

    def getLDAPServer(self, acl_folder):
        return acl_folder.getServers()[0].get('host', '')

    def getLDAPPort(self, acl_folder):
        return acl_folder.getServers()[0].get('port', '')

    def getRootDN(self, acl_folder):
        return acl_folder.groups_base

    def _user_dn_from_id(self, user_id):
        return "uid=%s,%s" % (user_id, self.getUserFolder().users_base)

    def _user_id_from_dn(self, dn):
        before = 'uid='
        after = ',%s' % self.getUserFolder().users_base

        assert dn.startswith(before) and dn.endswith(after)
        return dn[len(before):-len(after)]

    def getGroupScope(self, acl_folder):
        return acl_folder.groups_scope

    def get_ldap_delegate(self):
        acl_folder = self.getUserFolder()
        return acl_folder._delegate

    def getSortedUserRoles(self, skey='', rkey=''):
        """ sort users list """
        acl = self.getUserFolder()
        buf = []
        for user, value in self.getUsersRoles(acl).items():
            valid_values = [role_detail for role_detail in value if
                            role_detail[0][0] in self.list_valid_roles()]
            if not valid_values:
                continue
            user_info = self.get_source_user_info(user)
            if not user_info:
                log.warning("For getSortedUserRoles, Could not find user info for %s", user)
                continue
            is_disabled = user_info.status == 'disabled'
            buf.append((user, user_info.full_name,
                        self.getUserLocation(user), valid_values, is_disabled))
        if skey == 'user':
            return self.sort_list(buf, 0, rkey)
        elif skey == 'cn':
            return self.sort_list(buf, 1, rkey)
        elif skey == 'group':
            return self.sort_list(buf, 2, rkey)
        else:
            return buf

    def _parseRole(self, role):
        """Parse a structure like [('dn', {'cn':['value1'], 'description':['value2']})]
           and returns a tuple (dn, value1, value2)"""
        dn = role.get('dn', '')
        cn = role.get('cn', '')
        if cn:  cn = cn[0]
        description = role.get('description', '')
        if description:
            description = description[0].decode(self.default_encoding)
        return (dn, cn, description)

    def getRoles(self, expand=[LDAP_ROOT_ID], role_id=LDAP_ROOT_ID, depth=0):
        """Return a piece of roles tree"""
        role = self._user_objs[role_id]
        if role_id == LDAP_ROOT_ID:
            res = [(role, depth)]
            depth = depth + 1
        else:
            res = []
        if role_id in expand:
            #must expand this node
            if not role.cached:
                #must cache this node
                self._cacheRole(role)
            if role.cached:
                #this node is cached
                for child_role_id in role.childs:
                    res.append((self._user_objs[child_role_id], depth))
                    if self.isInList(expand, child_role_id):
                        res.extend(self.getRoles(expand, child_role_id, depth+1))
        return res

    def _searchRoles(self, dn):
        """Search roles in LDAP"""
        searchScope = ldap.SCOPE_ONELEVEL
        searchFilter = 'objectClass=*'
        ROLESretrieveAttributes = ('cn','description')
        delegate = self.get_ldap_delegate()
        roles = delegate.search(dn, searchScope, searchFilter, ROLESretrieveAttributes)
        return roles['results']

    def _cacheRole(self, role):
        """Cache a role"""
        #2. get all childs
        child_roles = self._searchRoles(role.dn)
        childs = []
        for child_role in child_roles:
            #3. parse
            child_role_dn, child_role_cn, child_role_description = self._parseRole(child_role)
            self._user_objs[child_role_cn] = ldap_user(child_role_cn, child_role_dn, child_role_cn, child_role_description, role.id, [], 0)
            childs.append(child_role_cn)
        #3. update current node
        role.childs = childs
        role.cached = 1
        self._p_changed = 1
        return 1

    def getLDAPSchema(self, acl_folder):
        """ returns the schema for a LDAPUserFolder """
        return acl_folder.getLDAPSchema()

    def getPluginPath(self):
        return self.absolute_url()

    def isList(self, l):
        return isinstance(l, list)

    security.declareProtected(manage_users, 'addUserRoles')
    def addUserRoles(self, name=[], roles=[], location='',
            user_location='', send_mail='', REQUEST=None):
        """ """
        super(plugLDAPUserFolder, self).addUserRoles(name, roles, location,
                user_location, send_mail, REQUEST)
        if REQUEST is not None:
            if is_ajax(REQUEST):
                url = (REQUEST['HTTP_REFERER'] +
                       ('?id=%s&s=assign_to_users' % self.id))
            else:
                url = REQUEST['HTTP_REFERER'] + '?id=' + self.id
            return REQUEST.RESPONSE.redirect(url)

    security.declareProtected(manage_users, 'revokeUserRoles')
    def revokeUserRoles(self, user, location, REQUEST=None):
        """ """
        super(plugLDAPUserFolder, self).revokeUserRoles(user, location, REQUEST)
        if REQUEST is not None:
            self.setSessionInfoTrans("Role(s) revoked")
            if is_ajax(REQUEST):
                url = REQUEST['HTTP_REFERER'] + '&s=manage_all'
            else:
                url = REQUEST['HTTP_REFERER']
            return REQUEST.RESPONSE.redirect(url)

    def get_groups_roles_map(self):
        groups_roles_map = {}
        def add_roles_from_ob(ob, is_brain=False):
            if is_brain:
                ob_roles = getattr(ob, 'ny_ldap_group_roles', MV)
                if not ob.has_key('ny_ldap_group_roles') or ob_roles is MV:
                    # catalog field (meta) not created or missing value in brain
                    is_brain = False
                    ob = ob.getObject()
            if not is_brain:
                try:
                    ob_roles = ob.acl_satellite.getAllLocalRoles()
                except AttributeError:
                    return # looks like we found a broken object
            elif ob_roles: # brain with roles, get the object
                ob = ob.getObject()
            for group_id, group_roles in ob_roles.iteritems():
                all_group_roles = groups_roles_map.setdefault(group_id, [])
                for role in group_roles:
                    location = {
                        'ob': ob,
                        'path': relative_object_path(ob, site),
                        'is_site': ob == site,
                    }
                    all_group_roles.append( (role, location) )

        site = self.getSite()
        add_roles_from_ob(site)
        for b in site.getCatalogTool()(path='/'):
            try:
                add_roles_from_ob(b, is_brain=True)
            except Unauthorized:
                pass # suppress restricted obs from breaking publishing

        return groups_roles_map

    def get_local_roles_by_groups(self, user):
        """
        Returns user local roles inside portal by being a member of a ldap
        group.
        Returns
        {'group': [('Role', {'ob': ob, 'path': path, 'is_site': bool}), ..],
         .. }
        where group index indicates the group that grants the role

        """
        local_roles = {}
        all_roles = self.get_groups_roles_map()
        user_in_group = self.getSite().acl_satellite.user_in_group_factory(user)
        for group, role_list in all_roles.items():
            if user_in_group(group):
                for role in role_list:
                    group_list = local_roles.setdefault(group, [])
                    group_list.append(role)
        return local_roles

    security.declareProtected(manage_users, 'map_group_to_role')
    def map_group_to_role(self, group, roles=[], location='',
            send_mail='', REQUEST=None):
        """ """
        def on_error(error_str):
            if REQUEST is not None:
                self.setSessionErrorsTrans(error_str)
                return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
            else:
                raise ValueError(error_str)

        if group == '':
            return on_error('No group selected')
        if roles == []:
            return on_error('No roles selected')

        if location == '/':
            location == ''
        try:
            ob = self.getSite().unrestrictedTraverse(location)
        except KeyError:
            return on_error('Invalid location path')
        ob.acl_satellite.add_group_roles(group, roles)

        if REQUEST is not None:
            manager_id = REQUEST.AUTHENTICATED_USER.getUserName()
            notify(RoleAssignmentEvent(ob, manager_id, group,
                                       roles, [], is_group=True,
                                       send_mail=send_mail))
            self.setSessionInfoTrans("Role(s) succesfully assigned")
            if is_ajax(REQUEST):
                url = REQUEST['HTTP_REFERER'] + '&s=assign_to_groups'
            else:
                url = REQUEST['HTTP_REFERER']
            return REQUEST.RESPONSE.redirect(url)

    security.declareProtected(manage_users, 'revoke_group_role')
    def revoke_group_role(self, group_id, role, location, REQUEST=None):
        """ """
        ob = self.getSite().unrestrictedTraverse(location)
        ob.acl_satellite.remove_group_roles(group_id, [role])

        if REQUEST is not None:
            manager_id = REQUEST.AUTHENTICATED_USER.getUserName()
            notify(RoleAssignmentEvent(ob, manager_id, group_id,
                                       [], [role], is_group=True,
                                       send_mail='Administrator'==role))
            self.setSessionInfoTrans("Role(s) revoked")
            if is_ajax(REQUEST):
                url = REQUEST['HTTP_REFERER'] + '&s=manage_all'
            else:
                url = REQUEST['HTTP_REFERER']
            return REQUEST.RESPONSE.redirect(url)

    @naaya_cache.timed(300)
    def group_member_ids(self, group):
        ldap_folder = self.getUserFolder()
        root_dn = self.getRootDN(ldap_folder)
        scope = self.getGroupScope(ldap_folder)
        delegate = self.get_ldap_delegate()
        result = delegate.search(root_dn, scope, filter_format('cn=%s', (group,)), ['uniqueMember'])
        if result['size'] > 0:
            group_user_members = result['results'][result['size']-1]['uniqueMember']
            group_users = []
            for member in group_user_members:
                if member == '':
                    continue # we found a placeholder member for empty groups
                try:
                    uid = member.split(',')[0].split('=')[1]
                except IndexError:
                    log.exception("Can't parse the uid %r, skipping", member)
                else:
                    group_users.append(uid)
            return group_users
        else:
            return []

    def user_in_group(self, user, group):
        return (str(user) in self.group_member_ids(group))

    def getUsersByRole(self, acl_folder, groups=None):
        """ Return all those users that are in a group """
        #all_dns = {}
        res = []
        res_append = res.append
        #member_attrs = GROUP_MEMBER_MAP.values()

        if groups is None:  return ()

        for group_id, group_dn in groups:
            dn = self.getRootDN(acl_folder)
            scope = self.getGroupScope(acl_folder)
            delegate = self.get_ldap_delegate()
            result = delegate.search(dn, scope, filter_format('(cn=%s)', (group_id,)), ['uniqueMember', 'member'])
            for val in result['results']:
                for dn in val['uniqueMember']:
                    p_username = self._user_id_from_dn(dn)
                    info = self.get_source_user_info(p_username)
                    res_append(info)
        return res

    def findLDAPUsers(self, acl_folder, params='', term='', role='', dn=''):
        """ search for users in LDAP """
        attrs=['employeeType'] + acl_folder.getSchemaConfig().keys()

        if self.REQUEST.has_key('search_user'):
            if params and term:
                try:
                    self.buffer = {}
                    users = acl_folder.findUser(search_param=params,
                                                search_term=term,
                                                attrs=attrs)
                    [self.buffer.setdefault(u['uid'],
                                            self.decode_cn(u['cn']))
                        for u in users if not u.get('employeeType') == 'disabled']
                    return [self.get_source_user_info(u['uid']) for u in users
                                if not u.get('employeeType') == 'disabled']
                except:
                    return ()
            else:
                return ()
        elif self.REQUEST.has_key('search_role'):
            try:
                self.buffer = {}
                users = self.getUsersByRole(acl_folder, [(role, dn)])
                [ self.buffer.setdefault(u.user_id, u.full_name) for u in users ]
                return users
            except:
                return ()
        else:
            return ()

    def getUserEmail(self, p_username, acl_folder):
        #return the email of the given user id
        try:
            user_info = self.get_source_user_info(p_username)
        except LDAPUserNotFound:
            return ''
        else:
            return user_info.email.encode(self.default_encoding)

    def getUserFullName(self, p_username, acl_folder):
        #return the full name of the given user id
        try:
            user_info = self.get_source_user_info(p_username)
        except LDAPUserNotFound:
            return ''
        else:
            if user_info is not None:
                return user_info.full_name.encode(self.default_encoding)
            else:
                log.warning("Could not retrieve user info  for %s", p_username)
                return p_username

    def decode_cn(self, value):
        if isinstance(value, str):
            value = value.decode(self.default_encoding)
        return value

    def get_group_roles_in_site(self, user):
        """
        The user may have site-level roles because they are part of an
        LDAP group. If so, return them.
        """
        return self.getSite().acl_satellite.getAdditionalRoles(user)

    def get_group_members(self, group_id):
        member_ids = self.group_member_ids(group_id)
        #ldap_user_folder = self.getUserFolder()

        def user_data(user_id):
            try:
                user_info = self.get_source_user_info(user_id)
            except LDAPUserNotFound:
                name = u"[not found]"
            else:
                name = user_info.full_name

            return {
                'user_id': user_id,
                'user_name': name,
            }

        return map(user_data, member_ids)

    def _get_zope_user(self, user_id):
        return self.getUserFolder().getUser(user_id)

    def get_source_user_info(self, user_id):
        # first, try to use the cache
        cached_record = ldap_cache.get(self._user_dn_from_id(user_id), None)
        if cached_record is not None:
            log.debug("loading user from cache: %r", user_id)
            return user_info_from_ldap_cache(user_id, cached_record, self)

        # not in cache, ask LDAPUserFolder
        zope_user = self._get_zope_user(user_id)
        if zope_user is None:
            raise LDAPUserNotFound(user_id)
        return user_info_from_zope_user(self, zope_user, self.default_encoding)

    def has_user(self, user_id):
        if ldap_cache.has(self._user_dn_from_id(user_id)):
            return True
        elif self._get_zope_user(user_id) is not None:
            return True
        else:
            return False

    security.declarePublic('interface_html')
    interface_html = PageTemplateFile('plugLDAPUserFolder', globals())

    security.declarePublic('section_manage_all_html')
    section_manage_all_html = PageTemplateFile('plugLDAPUserFolderManage', globals())

    security.declarePublic('section_assign_to_users_html')
    section_assign_to_users_html = PageTemplateFile('plugLDAPUserFolderAssignUsers', globals())

    security.declarePublic('section_assign_to_groups_html')
    section_assign_to_groups_html = PageTemplateFile('plugLDAPUserFolderAssignGroups', globals())

    security.declarePublic('section_group_members_html')
    section_group_members_html = PageTemplateFile('plugLDAPUserFolderGroupMembers', globals())

    security.declareProtected(manage_users, 'pickroles_html')
    pickroles_html = PageTemplateFile('pickRoles', globals())

InitializeClass(plugLDAPUserFolder)

class LdapSatelliteProvider(Acquisition.Implicit):
    """
    This class behaves like LDAPUserFolder's LDAPSatellite class, and manages
    local roles for LDAP groups. It is a singleton that has no state but uses
    acquisition wrappers to figure out from which folder it was accessed.
    """

    def getAllLocalRoles(self):
        current_folder = self.aq_parent
        return getattr(current_folder, '__ny_ldap_group_roles__', {})

    def user_in_group_factory(self, user):
        """
        Returns a function that checks whether `user` is part of the
        specified group.

          >>> user_in_group = self.user_in_group_factory(user)
          >>> user_in_group('group1')
          ... False
          >>> user_in_group('group2')
          ... True

        This factory is especially useful in testing, where it gets replaced
        with a simplified mock factory.
        """
        for auth_plugin in self.getSite().getAuthenticationTool().getSources():
            user_of_plugin = auth_plugin.getUserFolder().getUser(user.getId())
            # ideally we'd check ``if user_of_plugin is user``
            # but LDAPUserFolder returns a different instance of the
            # user object, so that doesn't work. Instead we just make sure
            # a user with the same ID exists in the plugin.
            if user_of_plugin is not None:
                return lambda group: auth_plugin.user_in_group(user, group)
        else:
            return lambda group: False

    def getAdditionalRoles(self, user):
        roles = set()
        user_in_group = self.user_in_group_factory(user)
        mapped_roles = self.getAllLocalRoles()
        for group in mapped_roles:
            if user_in_group(group):
                roles.update(mapped_roles[group])

        current_folder = self.aq_parent
        next_folder = current_folder.aq_inner.aq_parent
        next_satellite = getattr(next_folder, 'acl_satellite', None)
        if next_satellite is not None:
            roles.update(next_satellite.getAdditionalRoles(user))

        return list(roles)

    def add_group_roles(self, group, roles):
        assert not isinstance(roles, basestring), "Roles must be a list or tuple, not string"
        if not roles:
            return

        current_folder = self.aq_parent

        try:
            local_roles = current_folder.__ny_ldap_group_roles__
        except AttributeError:
            local_roles = current_folder.__ny_ldap_group_roles__ = {}

        if group not in local_roles:
            assigned_roles = local_roles[group] = []
        else:
            assigned_roles = local_roles[group]

        roles_to_add = []
        for role in roles:
            if role not in assigned_roles:
                roles_to_add.append(role)
        assigned_roles += roles_to_add
        #catalog = current_folder.getSite().getCatalogTool()
        #catalog.recatalogNyObject(current_folder)

        notify(NyAddGroupRoleEvent(current_folder, group, roles_to_add))

        current_folder._p_changed = True

    def remove_group_roles(self, group, roles):
        assert not isinstance(roles, basestring), "Roles must be a list or tuple, not string"

        current_folder = self.aq_parent
        local_roles = current_folder.__ny_ldap_group_roles__
        assigned_roles = local_roles[group]

        for role in roles:
            if role in assigned_roles:
                assigned_roles.remove(role)
            else:
                raise ValueError('Trying to remove non-existent role')
        if not assigned_roles:
            del local_roles[group]
        #catalog = current_folder.getSite().getCatalogTool()
        #catalog.recatalogNyObject(current_folder)

        notify(NyRemoveGroupRoleEvent(current_folder, group, roles))

        current_folder._p_changed = True

NySite.acl_satellite = LdapSatelliteProvider()

class LDAPUserInfo(UserInfo):
    """ a UserInfo with an extra property for LDAP (`dn`) """
    mandatory_fields = UserInfo.mandatory_fields | set(['dn', 'organisation',
            'postal_address', 'phone_number'])

def user_info_from_zope_user(ldap_plugin, zope_user, ldap_encoding):
    def extract(name):
        value = getattr(zope_user, name, '')
        if value is None:
            return ''
        return value.decode(ldap_encoding)
    fields = {
        'user_id': str(zope_user.id),
        'full_name': extract('cn'),
        'email': extract('mail'),
        'first_name': extract('givenName'),
        'last_name': extract('sn'),
        'organisation': extract('o'),
        'postal_address': extract('postalAddress'),
        'phone_number': extract('telephoneNumber'),
        'dn': extract('dn'),
        'status': extract('employeeType'),
        '_get_zope_user': lambda: zope_user,
        '_source': ldap_plugin,
    }
    return LDAPUserInfo(**fields)

def user_info_from_ldap_cache(user_id, cached_record, ldap_plugin):
    def get_zope_user():
        zope_user = ldap_plugin._get_zope_user(user_id)
        assert zope_user is not None, ("User loaded from cache but "
                                       "not found via LDAPUserFolder")
        return zope_user

    #encoding = ldap_plugin.default_encoding
    def extract(name):
        # encode values back to strings, because the rest of our ancient code
        # expects that.
        value = cached_record.get(name, u'')
        if isinstance(value, list):
            for i in value:
                assert isinstance(i, unicode), '%r not unicode' % i
        else:
            assert isinstance(value, unicode), '%r not unicode' % value
        return value

    try:
        get_zope_user()
    except AssertionError:
        return None

    fields = {
        'user_id': user_id,
        'full_name': extract('cn'),
        'email': extract('mail'),
        'first_name': extract('givenName'),
        'last_name': extract('sn'),
        'organisation': extract('o'),
        'postal_address': extract('postalAddress'),
        'phone_number': extract('telephoneNumber'),
        'dn': extract('dn'),
        'status': extract('employeeType'),
        '_get_zope_user': get_zope_user,
        '_source': ldap_plugin,
    }
    if 'jpegPhoto' in cached_record:
        fields['jpegPhoto'] = cached_record['jpegPhoto']
    return LDAPUserInfo(**fields)
