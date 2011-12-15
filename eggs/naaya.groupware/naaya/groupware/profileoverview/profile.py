from Products.Five.browser import BrowserView
from naaya.groupware.constants import METATYPE_GROUPWARESITE

from eea import usersdb


class ProfileClient(object):

    def __init__(self, zope_app, user, **config):
        self.zope_app = zope_app
        self.ldap_folder = zope_app.acl_users
        self.user = user
        servers = self.ldap_folder._delegate._servers
        config['ldap_server'] = servers[0]['host']
        self.agent = usersdb.UsersDB(**config)

    def access_in_igs(self):
        """
        Returns a dictonary of lists, key is access level,
        list contains IGs.

        """
        igs = self.zope_app.objectValues([METATYPE_GROUPWARESITE])
        roles = {}
        for ig in igs:
            access = ig.get_user_access(self.user)
            lst = roles.setdefault(access, [])
            lst.append(ig)
            lst.sort(key=lambda x: x.title_or_id())

        return roles

    def _dfs_roles_tree(self, tree):
        """
        Converts the tree structure of ldap roles (groups)
        to a list using DFS walk, useful for iteration in TAL

        """
        queue = [tree[k] for k in sorted(tree.keys(), reverse=True)]
        flat_structure = []
        while len(queue):
            current = queue.pop()
            flat_structure.append(current)
            if len(current['children']):
                current['children'].reverse()
                queue.extend(current['children'])

        return flat_structure

    def roles_tree_in_ldap(self):
        """
        Returns the ldap-roles that this user belongs to in LDAP.

        """
        ldap_roles = sorted(self.agent.member_roles_info(
                                   'user', self.user.getId(), ('description',)))
        tree = {}
        direct_address = {}
        for (role_id, attrs) in ldap_roles:
            role = {}
            role['id'] = role_id
            role['name'] = role_id.rsplit('-', 1)[-1]
            role['description'] = attrs['description'][0]
            role['level'] = 0
            role['parent'] = 'top'
            role['children'] = []
            direct_address[role_id] = role
            if '-' not in role_id:
                tree[role_id] = role
            else:
                parent = direct_address[role_id.rsplit('-', 1)[0]]
                parent['children'].append(role)
                parent['children'].sort(key=lambda x: x['name'])
                role['level'] = parent['level'] + 1
                role['parent'] = parent['id']
        return tree

    def roles_list_in_ldap(self):
        """
        Same as roles_tree_in_ldap, but result is a flat structure,
        a BFS walk of tree, useful for iteration in template

        """
        return self._dfs_roles_tree(self.roles_tree_in_ldap())


class ProfileView(BrowserView):

    def __call__(self, **kw):
        user = self.request.get('AUTHENTICATED_USER', None)
        # TODO: redirect here if user not logged in
        zope_app = self.context.unrestrictedTraverse('/')

        # TODO: this is a hack for devel
        user = zope_app.acl_users.getUser('fierefra')
        client = ProfileClient(zope_app, user)
        ig_access = client.access_in_igs()
        roles_list = client.roles_list_in_ldap()

        return self.index(ig_access=ig_access, roles=roles_list)
