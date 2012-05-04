from Products.naayaUpdater.updates import UpdateScript

permission_map = {
    'Publish content': 'Naaya - Publish content',
    'Manage Users': 'Manage users',
    'Validate content': 'Naaya - Validate content',
    'Edit content': 'Naaya - Edit content',
}

class RemovePermissionGroups(UpdateScript):
    title = 'Remove permission groups'
    authors = ['Alex Morega']
    creation_date = 'Aug 02, 2010'

    def _update(self, portal):
        portlets_tool = portal.getPortletsTool()

        for links_list in portlets_tool.objectValues(['Naaya Links List']):
            for id, item in links_list.get_links_collection().items():
                old_perm = item.permission
                if (not old_perm) or (old_perm in permission_map.values()):
                    # looks like it has already been updated
                    continue

                new_perm = permission_map[old_perm]
                pth = '/'.join(links_list.getPhysicalPath()) + ':' + id
                self.log.info('%r: %r -> %r', pth, old_perm, new_perm)
                item.permission = new_perm

            links_list._p_changed = True

        return True

class RemoveGhostRoles(UpdateScript):
    title = 'Remove roles of deleted users'
    authors = ['Valentin Dumitru']
    creation_date = 'Nov 11, 2010'

    def _update(self, portal):
        acl_users = portal.acl_users
        users_roles = _getUsersRoles(portal)
        for user, roles in users_roles.iteritems():
            if user not in acl_users.getUserNames() and not _get_user_by_uid(user, portal):
                for pair in roles:
                    location = portal.utGetObject(pair[1])
                    location.manage_delLocalRoles([user])
                    self.log.info('%r deleted for user %r for location %r', pair[0], user, pair[1])
        return True

def _getUsersRoles(portal):
    acl_users = portal.acl_users
    users_roles = {}
    p_meta_types = portal.get_containers_metatypes()
    for folder in _recurse(portal, p_meta_types):
        for roles_tuple in folder.get_local_roles():
            local_roles = acl_users.getLocalRoles(roles_tuple[1])
            if len(local_roles) > 0:
                if users_roles.has_key(str(roles_tuple[0])):
                    users_roles[str(roles_tuple[0])].append((local_roles, folder.absolute_url(1)))
                else:
                    users_roles[str(roles_tuple[0])] = [(local_roles, folder.absolute_url(1))]
    return users_roles

def _get_user_by_uid(user_id, portal):
    for source in portal.acl_users.getSources():
        acl_folder = source.getUserFolder()
        user_obj = acl_folder.getUser(user_id)
        if user_obj:
            return user_obj

def _recurse(ob, meta_types):
    for sub_ob in ob.objectValues(meta_types):
        yield sub_ob
        for o in _recurse(sub_ob, meta_types):
            yield o

class CorrectRolesForImportedUsers(UpdateScript):
    title = 'Correct role assignment for some users (imported with "" as role)'
    authors = ['Valentin Dumitru']
    creation_date = 'Oct 20, 2011'

    def _update(self, portal):
        auth_tool = portal.getAuthenticationTool()
        user_roles = auth_tool.getUsersRoles()
        user_with_invalid_roles = [user for user, roles in user_roles.items()
                if ([u''], '') in roles]
        if len(user_with_invalid_roles) > 0:
            auth_tool.admin_addroles(names=user_with_invalid_roles,
                    roles=['Contactpersoon coalitie biodiversiteit'])
            self.log.info('Updated roles for users: %s' % user_with_invalid_roles)
        else:
            self.log.info('No user roles to correct')
        return True

class AddNyLdapGroupRolesToCatalog(UpdateScript):
    title = 'Catalog ldap groups local roles'
    authors = ['Mihnea Simian']
    creation_date = 'May 03, 2012'

    def _update(self, portal):
        cat_tool = portal.getCatalogTool()
        if 'ny_ldap_group_roles' in cat_tool.schema():
            self.log.info('Portal already has this column in catalog, skipping')
        else:
            cat_tool.addColumn('ny_ldap_group_roles')
            cat_tool.refreshCatalog()
            self.log.info('Column added, catalog refreshed.')
        return True
