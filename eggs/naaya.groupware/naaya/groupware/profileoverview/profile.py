import operator
import urllib
try:
    import simplejson as json
except ImportError:
    import json

from Products.Five.browser import BrowserView
from naaya.groupware.constants import METATYPE_GROUPWARESITE
from Products.NaayaCore.AuthenticationTool.plugins import plugLDAPUserFolder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from eea.usersdb.factories import agent_from_uf

# limit the depth of search for notification subscriptions
CUTOFF_SUBS = 3

index_pt = PageTemplateFile('zpt/index.pt', globals())
ajax_roles_pt = PageTemplateFile('zpt/ig_roles_ajax.pt', globals())
subscriptions_pt = PageTemplateFile('zpt/subscriptions_ajax.pt', globals())

def get_plugldap(ig):
    """ Returns plugLDAPUserFolder in IG, None if not found """
    auth_tool = ig.getAuthenticationTool()
    sources = auth_tool.getSources()
    if not sources:
        return None
    for source in sources:
        if isinstance(source, plugLDAPUserFolder.plugLDAPUserFolder):
            return source
    return None


class ProfileClient(object):

    def __init__(self, zope_app, user, **config):
        assert user is not None, "ProfileClient got `user` argument None"
        self.zope_app = zope_app
        self.ldap_folder = zope_app.acl_users
        self.user = user
        self.agent = agent_from_uf(self.ldap_folder, **config)

    def access_in_igs(self):
        """
        Returns a dictonary of lists, key is access level,
        list contains IGs. We invoke groupware_site.get_user_access
        which relies on local roles stored in site object location

        """
        igs = self.zope_app.objectValues([METATYPE_GROUPWARESITE])
        roles = {}
        for ig in igs:
            access = ig.get_user_access(self.user)
            lst = roles.setdefault(access, [])
            lst.append(ig)
            lst.sort(key=lambda x: x.title_or_id())

        return roles

    def local_access_in_ig(self, ig):
        """
        Returns local roles user may have in corresponding ig.
        Return type: [{'location': obj, 'access': ['..'], 'group': ''}, ..]

        """
        auth_tool = ig.getAuthenticationTool()
        local_roles = auth_tool.getUserLocalRoles(self.user, try_groups=False)
        result = []
        for (roles, location) in local_roles:
            if location not in ('', '/'):
                result.append({'location': ig.unrestrictedTraverse(location),
                               'access': list(roles), 'group': ''})
        return result

    def local_roles_by_groups(self, ig):
        """
        The representation of results is the same as local_access_in_ig,
        but with 'group'
        Roles are looked up based on ldap roles and LDAPUserFolder groups.
        `leaf_roles_list` - terminal LDAP roles user belongs to

        """
        igs = self.zope_app.objectValues([METATYPE_GROUPWARESITE])
        result = []

        plugldap = get_plugldap(ig)
        if not plugldap:
            return []
        locals = plugldap.get_local_roles_by_groups(self.user)
        for group, roles in locals.items():
            for role, info in roles:
                result.append({'location': info['ob'], 'access': (role, ),
                               'group': group})
        return result

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
            role['description'] = attrs.get('description', ('', ))[0]
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
        a BFS walk of tree, useful for iteration in template.

        """
        return self._dfs_roles_tree(self.roles_tree_in_ldap())

    def notification_lists(self, igs, cutoff_level=None):
        """
        Returns a dictonary of lists, key is ig,
        list contains dicts of notifications info

        """
        notifications = {}
        for ig in igs:
            notif_tool = ig.getNotificationTool()
            ig_notifs = notif_tool.user_subscriptions(self.user, cutoff_level)
            if len(ig_notifs):
                ig_notifs.sort(key=lambda x: x['object'].title_or_id())
                notifications[ig] = ig_notifs

        return notifications

def get_profile(context, request, authenticated_user, zope_app):
    """
    Return LDAP user profile.
    If authenticated user is Manager, return the requested profile, otherwise
    return personal profile.
    """
    requested_user = request.form.get('user', None)
    if authenticated_user.has_role('Manager') and requested_user:
        user = zope_app.acl_users.getUser(requested_user)
        if not user:
            context.REQUEST.RESPONSE.notFoundError()
        return user
    else:
        return authenticated_user

def ProfileView(context, request):
    """
    If there's an AJAX request return user's IGs, else return user's roles and
    subscriptions.
    """
    auth_user = request.get('AUTHENTICATED_USER', None)
    is_ajax = request.form.get('ajax', None)
    ig_id = request.form.get('ig_id', None)

    if not auth_user.has_role('Authenticated'):
        if not is_ajax:
            referer = '/profile_overview?user=%s' % request.form.get('user', '')
            qs = urllib.urlencode({'came_from': referer})
            url = '/login/login_form?%s' % qs
            request.response.redirect(url)
            return None
        else:
            return ''

    zope_app = context.unrestrictedTraverse('/')
    user = get_profile(context, request, auth_user, zope_app)
    client = ProfileClient(zope_app, user)

    if not is_ajax:
        roles_list = client.roles_list_in_ldap()
        leaf_roles_list = [ r for r in roles_list if not r['children'] ]
        return index_pt.__of__(context)(roles=leaf_roles_list,
                                        user_id=user.getId())
    elif is_ajax == 'igs':
        ig_access = client.access_in_igs()

        if 'restricted' in ig_access:
            del ig_access['restricted']
        all_igs = []
        for igs in ig_access.values():
            all_igs.extend(igs)
        return json.dumps([ig.getId() for ig in all_igs])

    elif is_ajax == 'memberships':
        ig_access = client.access_in_igs()

        if 'restricted' in ig_access:
            del ig_access['restricted']
        ig_details = {}
        roles = set()
        ig = client.zope_app[ig_id]
        ig_details[ig.id] = client.local_access_in_ig(ig)
        by_groups = client.local_roles_by_groups(ig)
        roles.update(set(map(operator.itemgetter('group'), by_groups)))
        ig_details[ig.id].extend(by_groups)

        if not ig_details[ig.id] and ig_access.has_key('viewer'):
            ig_access['viewer'].remove(ig)
        role_names = {}
        for role in roles:
            role_names[role] = client.agent.role_info(role)['description']

        user_roles = []
        for k,v in ig_access.items():
            if ig in v:
                user_roles.append(k)
        return ajax_roles_pt.__of__(context)(ig=ig,
                                             ig_details=ig_details,
                                             user_roles=user_roles,
                                             role_names=role_names)
    elif is_ajax == 'subscriptions':
        ig_access = client.access_in_igs()
        if 'restricted' in ig_access:
            del ig_access['restricted']
        ig = client.zope_app[ig_id]
        notifications = client.notification_lists([ig], CUTOFF_SUBS)
        return subscriptions_pt.__of__(context)(ig=ig,
                                                sorted_func=sorted,
                                                subscriptions=notifications,
                                                user_id=user.getId())

def show_local_roles(context, request):
    """ method for Eionet Full Profile """
    userid = request.form.get('userid')
    zope_app = context.unrestrictedTraverse("/")
    user = zope_app.acl_users.getUser(userid)
    client = ProfileClient(zope_app, user)
    ig_access = client.access_in_igs()

    if 'restricted' in ig_access:
        del ig_access['restricted']
    all_igs = []
    roles = set()
    for igs in ig_access.values():
        all_igs.extend(igs)
    result = []
    for ig in all_igs:
        auth_tool = ig.getAuthenticationTool()
        local_roles = auth_tool.getUserLocalRoles(user, try_groups=False)
        for (roles, location) in local_roles:
            location = ig.unrestrictedTraverse(location)
            if location != ig:
                title = '%s > %s' % (ig.title_or_id(), location.title_or_id())
            else:
                title = location.title_or_id()
            result.append({'roles': roles, 'ob_url': location.absolute_url(),
                           'ob_title': title,
                           'extra': {'ig': ig.getId()}})
    request.RESPONSE.setHeader('Content-type', 'application/json')
    return json.dumps({userid: result})
