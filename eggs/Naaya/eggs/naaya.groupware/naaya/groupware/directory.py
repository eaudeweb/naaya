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
    def search_directory(self, search_string=u'', REQUEST=None):
        """ """
        users = self.get_users()
        if not search_string:
            user_list = users
        else:
            search_string = search_string.lower()
            user_list = [user for user in users if \
                         search_string in user['firstname'].lower() or \
                         search_string in user['lastname'].lower() or \
                         search_string in user['userid'].lower()]
        return self.index_html(user_list=user_list)

    def get_users(self):
        if not hasattr(self, '_v_external_user_cache'):
            self._v_external_user_cache = {}
        cache = self._v_external_user_cache
        users = []

        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        self.update_sources_cache(acl_tool)

        local_users = acl_tool.getUsers()
        external_users = []
        for source_id in self.sources.keys():
            source = self.sources[source_id]['source']
            individual_users = self.sources[source_id]['user_roles'].keys()

            group_users = []
            for group_id in self.sources[source_id]['group_map'].keys():
                group_users.extend(
                    source.group_member_ids(group_id)
                )

            combined_users = individual_users + group_users
            for userid in combined_users:

                if cache.get(userid, {}):
                    user_dict = cache[userid]
                else:
                    user_dict = source._get_user_by_uid(userid,
                                                        source.getUserFolder())
                    cache[userid] = user_dict

                user_roles = self.get_external_user_roles(source, userid)
                user_dict['access_level'] = \
                         self.get_user_access_level(user_roles)

                external_users.append(user_dict)

        def handle_unicode(s):
            if not isinstance(s, unicode):
                try:
                    return s.decode('utf-8')
                except:
                    return s.decode('latin-1')
            else:
                return s

        for user in local_users:
            user_roles = self.get_local_user_roles(user)
            users.append({
                'userid': user.name,
                'firstname': handle_unicode(user.firstname),
                'lastname': handle_unicode(user.lastname),
                'email': user.email,
                'access_level': self.get_user_access_level(user_roles),
                'organisation': 'N/A',
                'postal_address': 'N/A',
            })

        for user in external_users:
            users.append({
                'userid': user['uid'],
                'firstname': handle_unicode(user['givenName']),
                'lastname': handle_unicode(user['sn']),
                'email': user['mail'],
                'access_level': user['access_level'],
                'organisation': user.get('o', 'N/A'),
                'postal_address': handle_unicode(
                                    user.get('postalAddress', 'N/A')
                                  ),
            })
        self._v_user_cache = users
        return users

    def get_local_user_roles(self, userob):
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        return acl_tool.getUserRoles(userob)

    def get_external_user_roles(self, source, userid):
        individual_ldap_users = self.sources[source.id]['user_roles']
        group_to_role_mapping = self.sources[source.id]['group_map']
        site_id = self.getSite().getId()
        roles = []
        if userid in individual_ldap_users.keys():
            for role in individual_ldap_users[userid]:
                if role[1].endswith(site_id):
                    roles.extend(role[0])
        for groupid in group_to_role_mapping.keys():
            if userid in source.group_member_ids(groupid):
                for role, role_location in group_to_role_mapping[groupid]:
                    if not role_location['is_site']:
                        continue
                    roles.append(role)
        return roles

    def get_user_info(self, userid):
        if not hasattr(self, '_v_user_cache'):
            self.get_users()
        for user in self._v_user_cache:
            if user['userid'] != userid:
                continue
            return user

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

    index_html = PageTemplateFile('zpt/directory_index', globals())
    user_details = PageTemplateFile('zpt/directory_user_details', globals())

InitializeClass(Directory)
