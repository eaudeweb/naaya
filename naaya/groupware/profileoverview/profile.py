from Products.Five.browser import BrowserView
from naaya.groupware.constants import METATYPE_GROUPWARESITE

from eea import usersdb


class ProfileClient(object):

    def __init__(self, zope_app, user, **config):
        assert user is not None, "ProfileClient got `user` argument None"
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
        queue = [tree[k] for k in sorted(tree.keys())]
        flat_structure = []
        while queue:
            current = queue.pop(0)
            flat_structure.append(current)
            if current['children']:
                new_queue = list(current['children'])
                new_queue.extend(queue)
                queue = new_queue

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
            role['children'] = []
            direct_address[role_id] = role
            if '-' not in role_id:
                tree[role_id] = role
                role['level'] = 0
                role['parent'] = 'top'
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

    def notification_lists(self):
        """
        Returns a dictonary of lists, key is ig,
        list contains dicts of notifications info

        """
        igs = self.zope_app.objectValues([METATYPE_GROUPWARESITE])
        notifications = {}
        for ig in igs:
            notif_tool = ig.getNotificationTool()
            ig_notifs = notif_tool.user_subscriptions(self.user)
            if len(ig_notifs):
                ig_notifs.sort(key=lambda x: x['object'].title_or_id())
                notifications[ig] = ig_notifs

        return notifications

class ProfileView(BrowserView):

    def __call__(self, **kw):
        user = self.request.get('AUTHENTICATED_USER', None)
        if not user.has_role('Authenticated'):
            # TODO: nicer redirect
            url = '/login/login_form?came_from=%s' % '/profile'
            self.request.response.redirect(url)
            return None
        zope_app = self.context.unrestrictedTraverse('/')

        client = ProfileClient(zope_app, user)
        roles_list = client.roles_list_in_ldap()
        notifications = client.notification_lists()
        ig_access = client.access_in_igs()

        # custom filters - only relevant info in view
        leaf_roles_list = [ r for r in roles_list if not r['children'] ]
        if 'viewer' in ig_access:
            del ig_access['viewer']
        if 'restricted' in ig_access:
            del ig_access['restricted']

        return self.index(ig_access=ig_access, roles=leaf_roles_list,
                          subscriptions=notifications)

class DemoProfileView(BrowserView):

    def __call__(self, **kw):
        user = self.request.get('AUTHENTICATED_USER', None)
        if not user.has_role('Authenticated'):
            # TODO: nicer redirect
            url = '/login/login_form?came_from=%s' % '/profile'
            self.request.response.redirect(url)
            return None
        zope_app = self.context.unrestrictedTraverse('/')

        # TODO: this is a hack for devel
        user = zope_app.acl_users.getUser('parttpet')
        client = ProfileClient(zope_app, user)
        ig_access = client.access_in_igs()

        # TODO: this is a hack for devel
        user = zope_app.acl_users.getUser('fierefra')
        client = ProfileClient(zope_app, user)
        roles_list = client.roles_list_in_ldap()
        notifications = client.notification_lists()

        # custom filters - only relevant info in view
        leaf_roles_list = [ r for r in roles_list if not r['children'] ]
        if 'viewer' in ig_access:
            del ig_access['viewer']
        if 'restricted' in ig_access:
            del ig_access['restricted']

        return self.index(ig_access=ig_access, roles=leaf_roles_list,
                          subscriptions=notifications)
