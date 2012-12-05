""" Provides logic to overview security settings """

from copy import deepcopy

from AccessControl.Permission import Permission
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from naaya.core.zope2util import ofs_path


def allowed(context, permission=None):
    """
    Roles that have `permission` and why.
    Returns {PERM_NAME: {'Role': (REASON, META), ..}, ..}
    where `REASON` in ('assigned', 'inherited').
    `META` can be None or dict supplying extra info, like `source` of
    permission inheritance.

    """
    out = {}
    all_roles = context.valid_roles()
    permissions = context.ac_inherited_permissions(1)
    if permission:
        permissions = [x for x in permissions if x[0] == permission]
    for perm in permissions:
        name, value = perm[:2]
        maps = out[name] = {}
        perm = Permission(name, value, context)
        roles = perm.getRoles(default=[])

        for role in roles:
            maps[role] = ('assigned', None)

        if isinstance(roles, list):
            for role in set(all_roles) - set(roles):
                from_parent = allowed(context.aq_parent, name)
                parent_permission = from_parent[name].get(role)
                if parent_permission:
                    reason, meta = parent_permission
                    if reason == 'assigned':
                        maps[role] = ('inherited',
                                      {'source': ofs_path(context.aq_parent)})
                    elif reason == 'inherited':
                        maps[role] = parent_permission
    return out

def allowed2(context, permission=None):
    """
    Higher level of :meth:`.allowed`
    It takes in consideration the Anonymous/Authenticated implications.
    Extra value for reason: 'pseudorole'.

    """
    all_roles = context.valid_roles()
    settings = allowed(context, permission)
    out = deepcopy(settings)
    for permission, role_map in settings.items():
        if 'Authenticated' in role_map:
            for role in set(all_roles) - set(['Anonymous', 'Authenticated']):
                out[permission][role] = ('pseudorole', {'source': 'Authenticated'})
        if 'Anonymous' in role_map:
            for role in set(all_roles) - set(['Anonymous']):
                out[permission][role] = ('pseudorole', {'source': 'Anonymous'})
    return out

# views
def access_overview(context, request=None):
    """ Render the overview template (widget) """
    settings = allowed2(context, 'View')['View']
    for role, mapping in settings.items():
        if mapping[0] == 'inherited':
            mapping[1]['source'] = \
               context.unrestrictedTraverse(mapping[1]['source'])

    return settings
