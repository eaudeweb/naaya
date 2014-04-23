from operator import itemgetter

from Acquisition import Implicit
from OFS.SimpleItem import Item
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.AuthenticationTool.plugins.plugLDAPUserFolder \
     import plugLDAPUserFolder
from Products.NaayaCore.AuthenticationTool.plugins import ldap_cache
from Products.NaayaCore.managers.import_export import generate_csv, generate_excel
from naaya.core.utils import force_to_unicode
from eea.usersdb.factories import agent_from_uf

class MemberSearch(Implicit, Item):
    title = "Interest Group member search"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declarePrivate('get_sources_info')
    def get_sources_info(self, acl_tool):
        ret = {}
        for source in acl_tool.getSources():
            if not isinstance(source, plugLDAPUserFolder):
                continue
            source_uf = source.getUserFolder()
            individual_ldap_users = source.getUsersRoles(source_uf)
            group_to_role_mapping = source.get_groups_roles_map()
            ret[source.id] = {
                'user_roles': individual_ldap_users,
                'group_map': group_to_role_mapping,
                'source': source,
            }
        return ret

    def _search_users(self, search_string=u'', sort_by='', reverse_sort=False):
        search_string = search_string.lower()
        local_users_list = self.search_local_users(search_string)
        external_users_list = self.search_external_users(search_string)
        user_list = local_users_list + external_users_list
        if sort_by:
            user_list.sort(key=itemgetter(sort_by), reverse=reverse_sort)
        return user_list

    security.declareProtected(view, 'search_users_html')
    def search_users_html(self, search_string=u'', sort_by='',
            reverse_sort='False', only_admins=False):
        """ """
        reverse_sort = reverse_sort != 'False'
        user_list = self._search_users(search_string, sort_by, reverse_sort)
        if only_admins:
            user_list = [user for user in list(user_list)
                            if 'Administrator' in user['access_level'].split(', ')]
        return self.user_list_html(search_string=search_string,
                                   sorted_by=sort_by,
                                   reverse_sorted=reverse_sort,
                                   user_list=user_list)

    security.declarePrivate('search_local_users')
    def search_local_users(self, search_string=u''):
        ret = []
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        local_users = acl_tool.getUsers()
        search_string = search_string.lower().strip()
        for user in local_users:
            if (search_string in user.name.lower() or
                search_string in user.firstname.lower() or
                search_string in user.lastname.lower()
                ):
                ret.append(self.get_local_user_info(user))
        return ret

    security.declarePrivate('search_external_users')
    def search_external_users(self, search_string=u''):
        ret = []
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        sources_info = self.get_sources_info(acl_tool)

        for source_id in sources_info.keys():
            source = sources_info[source_id]['source']

            individual_userids = sources_info[source_id]['user_roles'].keys()
            group_userids_map = self.get_group_userids_map(source_id,
                                                           sources_info)
            group_userids = []
            for group_users in group_userids_map.values():
                group_userids.extend(group_users)
            userids = set(individual_userids + group_userids)

            if search_string.strip():
                agent = agent_from_uf(source.getUserFolder())
                users = agent.search_user(search_string)
                users = [user for user in users if
                            user.get('uid', user.get('id', None)) and
                         user.get('uid', user.get('id')) in userids]
            else:
                cache = ldap_cache.Cache()
                cache.update()
                users = []

                for user_dn in cache.users:
                    user = cache.get(user_dn)
                    if user.has_key('uid') and user['uid'] in userids:
                        users.append({
                        'id': user['uid'],
                        'first_name': user['givenName'],
                        'last_name': user['sn'],
                        'full_name': user['cn'],
                        'email': user.get('mail', ''),
                        'organisation': user.get('o', 'N/A'),
                        'postal_address': user.get('postalAddress', 'N/A'),
                        })

            # precalculate user roles for performance
            user_roles_map = {}
            for user in users:
                user_id = user.get('uid', user.get('id'))
                user_roles = self.get_external_user_roles(
                                source,
                                user_id,
                                sources_info,
                                group_userids_map)
                user_roles_map[user_id] = user_roles

            user_info = [self.get_external_user_info(
                            source, user,
                            user_roles_map[user.get('uid', user.get('id'))])
                         for user in users]

            ret.extend(user_info)

        return ret

    security.declarePrivate('get_user_info')
    def get_user_info(self, userid):
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        user = acl_tool.getUser(userid)
        if user is not None:
            return self.get_local_user_info(user)

        sources_info = self.get_user_info(acl_tool)
        for source_id in sources_info.keys():
            source = sources_info[source_id]['source']
            acl_folder = source.getUserFolder()
            user = acl_folder.getUserById(userid, None)
            if user is not None:
                return self.get_external_user_info(source, user._properties)

    security.declarePrivate('get_local_user_info')
    def get_local_user_info(self, user):
        user_roles = self.get_local_user_roles(user)
        firstname = force_to_unicode(user.firstname)
        lastname = force_to_unicode(user.lastname)
        name = firstname + u' ' + lastname
        return {
                'userid': user.name,
                'firstname': force_to_unicode(user.firstname),
                'lastname': force_to_unicode(user.lastname),
                'name': name,
                'email': user.email,
                'access_level': self.get_user_access_level(user_roles),
                'organisation': 'N/A',
                'postal_address': 'N/A',
                }

    security.declarePrivate('get_external_user_info')
    def get_external_user_info(self, source, user, user_roles=None):
        user_id = user.get('uid', user.get('id'))
        # user_roles are precalculated for the member search (perfomance)
        if user_roles is None:
            user_roles = self.get_external_user_roles(source, user_id)
        return {
                'userid': user_id,
                'firstname': force_to_unicode(user['first_name']),
                'lastname': force_to_unicode(user['last_name']),
                'name': force_to_unicode(user['full_name']),
                'email': user['email'],
                'access_level': self.get_user_access_level(user_roles),
                'organisation': force_to_unicode(
                                user.get('organisation', 'N/A')),
                'postal_address': force_to_unicode(
                                user.get('postal_address', 'N/A')),
                }

    security.declarePrivate('get_local_user_roles')
    def get_local_user_roles(self, userob):
        portal = self.getSite()
        acl_tool = portal.getAuthenticationTool()
        return acl_tool.getUserRoles(userob)

    security.declarePrivate('get_external_user_roles')
    def get_external_user_roles(self, source, userid, sources_info,
                                group_userids_map=None):
        # group_userids_map is precalculated for member search (performance)
        if group_userids_map is None:
            group_userids_map = self.get_group_userids_map(source.id,
                                                           sources_info)
        individual_ldap_users = sources_info[source.id]['user_roles']
        group_to_role_mapping = sources_info[source.id]['group_map']
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

    security.declarePrivate('get_group_userids_map')
    def get_group_userids_map(self, source_id, sources_info):
        group_userids_map = {}
        source = sources_info[source_id]['source']
        for group_id in sources_info[source_id]['group_map'].keys():
            group_userids_map[group_id] = source.group_member_ids(group_id)
        return group_userids_map

    security.declarePrivate('get_user_access_level')
    def get_user_access_level(self, roles):
        if len(roles) == 0:
            return u'N/A'
        else:
            return u', '.join(roles)

    security.declareProtected(view, 'is_member')
    def is_member(self):
        """ """
        return self.get_user_access() in ['member', 'admin']

    security.declareProtected(view, 'download')
    def download(self, RESPONSE, search_string=u'', sort_by='',
            reverse_sort='False', file_type='CSV'):
        """returns all the search results in a csv or excel file"""
        reverse_sort = reverse_sort != 'False'
        users = self._search_users(search_string, sort_by, reverse_sort)

        if self.is_member():
            header = ['Name', 'Organisation', 'Postal address', 'Email',
                              'Access level', 'User ID']
            rows = [[user['name'], user['organisation'], user['postal_address'],
                     user['email'], user['access_level'], user['userid']]
                    for user in users]
        else:
            header = ['Name', 'Organisation']
            rows = [[user['name'], user['organisation']]
                    for user in users]

        if file_type == 'CSV':
            RESPONSE.setHeader('Content-Type', 'text/csv')
            RESPONSE.setHeader('Content-Disposition',
                               'attachment; filename=%s.csv' % self.id)
            return generate_csv(header, rows)
        elif file_type == 'Excel' and self.rstk.we_provide('Excel export'):
            RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
            RESPONSE.setHeader('Content-Disposition',
                               'attachment; filename=%s.xls' % self.id)
            return generate_excel(header, rows)
        else:
            raise ValueError('unknown file format %r' % file_type)


    index_html = PageTemplateFile('zpt/member_search_index', globals())
    user_list_html = PageTemplateFile('zpt/member_search_list', globals())

InitializeClass(MemberSearch)
