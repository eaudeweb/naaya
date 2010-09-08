from operator import itemgetter

from Acquisition import Implicit
from OFS.SimpleItem import Item
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.AuthenticationTool.plugins.plugLDAPUserFolder \
     import plugLDAPUserFolder


class Directory(Implicit, Item):
    title = "Interest Group Directory"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id
        self.sources = {}

    def update_sources_cache(self, acl_tool):
        for source in acl_tool.getSources():
            if not isinstance(source, plugLDAPUserFolder):
                continue
            source_uf = source.getUserFolder()
            individual_ldap_users = source.getUsersRoles(source_uf)
            group_to_role_mapping = source.get_groups_roles_map()
            self.sources[source.id] = {
                'user_roles': individual_ldap_users,
                'group_map': group_to_role_mapping,
                'source': source,
            }

    security.declareProtected(view, 'search_directory')
    def search_directory(self, search_string=u'', sort_by='',
            reverse_sort='False'):
        """ """
        search_string = search_string.lower()
        reverse_sort = reverse_sort != 'False'
        local_users_list = self.search_local_users(search_string)
        external_users_list = self.search_external_users(search_string)
        user_list = local_users_list + external_users_list
        if sort_by:
            user_list.sort(key=itemgetter(sort_by), reverse=reverse_sort)
        return self.user_list_html(search_string=search_string,
                                   sorted_by=sort_by,
                                   reverse_sorted=reverse_sort,
                                   user_list=user_list)

    def search_local_users(self, search_string=u''):
        ret = []
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        local_users = acl_tool.getUsers()
        for user in local_users:
            if search_string in user.name.lower():
                ret.append(self.get_local_user_info(user))
        return ret

    def search_external_users(self, search_string=u''):
        ret = []
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        self.update_sources_cache(acl_tool)
        for source_id in self.sources.keys():
            source = self.sources[source_id]['source']

            individual_userids = self.sources[source_id]['user_roles'].keys()
            group_userids_map = self.get_group_userids_map(source_id)
            group_userids = []
            for group_users in group_userids_map.values():
                group_userids.extend(group_users)
            userids = set(individual_userids + group_userids)

            users = source.getUserFolder().findUser('cn', search_string)
            users = [user for user in users if user['uid'] in userids]

            # precalculate user roles for performance
            user_roles_map = {}
            for user in users:
                user_roles = self.get_external_user_roles(source, user['uid'],
                                                          group_userids_map)
                user_roles_map[user['uid']] = user_roles

            user_info = [self.get_external_user_info(source, user,
                                                 user_roles_map[user['uid']])
                          for user in users]

            ret.extend(user_info)

        return ret

    def get_user_info(self, userid):
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        user = acl_tool.getUser(userid)
        if user is not None:
            return self.get_local_user_info(user)

        self.update_sources_cache(acl_tool)
        for source_id in self.sources.keys():
            source = self.sources[source_id]['source']
            acl_folder = source.getUserFolder()
            user = acl_folder.getUserById(userid, None)
            if user is not None:
                return self.get_external_user_info(source, user._properties)

    def get_local_user_info(self, user):
        user_roles = self.get_local_user_roles(user)
        firstname = handle_unicode(user.firstname)
        lastname = handle_unicode(user.lastname)
        name = firstname + u' ' + lastname
        return {
                'userid': user.name,
                'firstname': handle_unicode(user.firstname),
                'lastname': handle_unicode(user.lastname),
                'name': name,
                'email': user.email,
                'access_level': self.get_user_access_level(user_roles),
                'organisation': 'N/A',
                'postal_address': 'N/A',
                }

    def get_external_user_info(self, source, user, user_roles=None):
        # user_roles are precalculated for the search directory (perfomance)
        if user_roles is None:
            user_roles = self.get_external_user_roles(source, user['uid'])
        return {
                'userid': user['uid'],
                'firstname': handle_unicode(user['givenName']),
                'lastname': handle_unicode(user['sn']),
                'name': handle_unicode(user['cn']),
                'email': user.get('mail', ''),
                'access_level': self.get_user_access_level(user_roles),
                'organisation': handle_unicode(user.get('o', 'N/A')),
                'postal_address': handle_unicode(
                                    user.get('postalAddress', 'N/A')
                                  ),
                }

    def get_local_user_roles(self, userob):
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        return acl_tool.getUserRoles(userob)

    def get_external_user_roles(self, source, userid, group_userids_map=None):
        # group_userids_map is precalculated for search directory (performance)
        if group_userids_map is None:
            group_userids_map = self.get_group_userids_map(source.id)
        individual_ldap_users = self.sources[source.id]['user_roles']
        group_to_role_mapping = self.sources[source.id]['group_map']
        site_id = self.getSite().getId()
        roles = []
        if userid in individual_ldap_users.keys():
            for role in individual_ldap_users[userid]:
                if role[1].endswith(site_id):
                    roles.extend(role[0])
        for groupid in group_to_role_mapping.keys():
            if userid in group_userids_map[groupid]:
                for role, role_location in group_to_role_mapping[groupid]:
                    if not role_location['is_site']:
                        continue
                    roles.append(role)
        return roles

    def get_group_userids_map(self, source_id):
        group_userids_map = {}
        source = self.sources[source_id]['source']
        for group_id in self.sources[source_id]['group_map'].keys():
            group_userids_map[group_id] = source.group_member_ids(group_id)
        return group_userids_map

    def get_user_access_level(self, roles):
        access_level = 'N/A'
        if 'Contributor' in roles:
            access_level = 'Contributor'
        if 'Administrator' in roles:
            access_level = 'Administrator'
        if 'Manager' in roles:
            access_level = 'Manager'
        if 'Viewer' in roles:
            access_level = 'Viewer'
        return access_level

    def is_member(self):
        return self.get_user_access() in ['member', 'admin']

    index_html = PageTemplateFile('zpt/directory_index', globals())
    user_list_html = PageTemplateFile('zpt/directory_user_list', globals())

InitializeClass(Directory)


def handle_unicode(s):
    if not isinstance(s, unicode):
        try:
            return s.decode('utf-8')
        except:
            return s.decode('latin-1')
    else:
        return s
