from StringIO import StringIO
from zipfile import ZipFile

import backupdata

from naaya.core.zope2util import relative_object_path

def work_in_zope(context, name, root_path):
    """
    Call this method from a Zope ExternalMethod. It assumes a local
    folder that has CIRCA-exported Zip files (using the "save" method,
    not "download"). Call it from the Web and pass in a "name" parameter
    which is the filename you want to import. Make sure you call the
    external method in the context of a folder where you want the files
    to be imported.

    Example external method code::
        from edw.circaimport import work_in_zope
        def do_import(self, REQUEST):
            name = REQUEST.get('name')
            return work_in_zope(self, name, '/path/to/downloads/folder')
    """
    from actors import ZopeActor
    assert '/' not in name and name != '..'
    zip_path = root_path + '/' + name
    zip_fs_file = open(zip_path, 'rb')
    report = StringIO()

    zf = ZipFile(zip_fs_file)
    index_file = StringIO(zf.read('index.txt'))
    current_user = context.REQUEST.AUTHENTICATED_USER.getId()
    actor = ZopeActor(context, report, current_user)
    def open_backup_file(name):
        return StringIO(zf.read(name))

    backupdata.walk_backup(index_file, open_backup_file, actor)

    actor.finished()

    zip_fs_file.close()
    return report.getvalue()

def add_roles_from_circa_export(site, filepath, ldap_source_title):
    from ldif_extract import get_user_and_group_mapping
    user_2_role, group_2_role = get_user_and_group_mapping(filepath)

    auth_tool = site.getAuthenticationTool()
    for source in auth_tool.getSources():
        if source.title == ldap_source_title:
            ldap_source = source
            break
    else:
        return 'Error: No user source named %s' % ldap_source_title

    report = StringIO()
    for userid, role in user_2_role.items():
        if not ldap_source.has_user(userid):
            print>>report, 'Error: no user named %s in source %s' % (userid, ldap_source_title)
            continue

        try:
            ldap_source.addUserRoles(userid, [role])
        except Exception, e:
            print>>report, 'Error adding role %s for user %s: %s' % (role, userid, e)
        else:
            print>>report, 'Added role %s for user %s' % (role, userid)

    for groupid, role in group_2_role.items():
        try:
            ldap_source.map_group_to_role(groupid, [role])
        except Exception, e:
            print>>report, 'Error adding role %s for group %s: %s' % (role, groupid, e)
        else:
            print>>report, 'Added role %s for group %s' % (role, groupid)

    return report.getvalue()

def add_notifications_from_circa_export(site, filepath):
    from notifications_extract import get_notifications_mapping
    dbfile = open(filepath, 'rb')
    notifications, not_matched = get_notifications_mapping(dbfile)
    dbfile.close()

    notif_tool = site.getNotificationTool()
    auth_tool = site.getAuthenticationTool()
    report = StringIO()
    for user_id, values in notifications.items():
        user = auth_tool.get_user_with_userid(user_id)
        if user is None:
            print>>report, 'Error: user not found: %s' % user_id
            continue

        for val in values:
            if val['notif_type'] == 3:
                print>>report, 'Ignoring (turned off) subscription for user %s at location %s' % (user_id, val['path'])
                continue

            try:
                ob = site.unrestrictedTraverse(val['path'].strip('/'))
            except KeyError:
                print>>report, "Couldn't find object at path: %s" % val['path']
                continue

            location = relative_object_path(ob, site)
            try:
                notif_tool.add_account_subscription(user_id,
                                                    location,
                                                    'instant', 'en')
            except ValueError, msg:
                print>>report, 'Error adding subscription for user %s at location %s: %s' % (user_id, val['path'], msg)
                continue

            print>>report, 'Added subscription for user %s at location %s' % (user_id, val['path'])

    return report.getvalue()

def add_acls_from_circa_export(site, filepath):
    from AccessControl.Permissions import view
    from AccessControl.Permission import Permission
    from acl_extract import get_acl_mapping

    auth_tool = site.getAuthenticationTool()
    def set_acl_for_user(ob, user):
        ldap_source_title = auth_tool.getUserSource(user)
        location = relative_object_path(ob, site)
        for source in auth_tool.getSources():
            if source.title == ldap_source_title:
                ldap_source = source
                ldap_source.addUserRoles(str(user), ['Viewer'], location)
                break

    def set_acl_for_roles(ob, roles):
        permission_object = Permission(view, (), ob)
        current_roles = permission_object.getRoles()
        is_tuple = isinstance(current_roles, tuple)
        current_roles = list(current_roles)
        new_roles = set(roles + current_roles)
        if is_tuple:
            new_roles = tuple(new_roles)
        else:
            new_roles = list(new_roles)
        permission_object.setRoles(new_roles)

    ROLES_MAPPING = {'0': 'Administrator',
            '1': 'Viewer',
            '2': 'Contributor',
            '3': 'Viewer',
            '4': 'Viewer'}
    def compute_roles_mapping(acls):
        """
        Computes the ROLES_MAPPING variable based on:
        https://svn.eionet.europa.eu/projects/Zope/ticket/4095#comment:10

        The last 2 roles are 'Anonymous' and 'Authenticated':
            any other roles are added before those
        """
        non_userids = []
        for values in acls.values():
            non_userids.extend([val for val in values if not val.endswith('@circa')])
        roles = [val[2:] for val in non_userids if val.startswith('__')]
        roles = list(set(roles)) # remove duplicates
        roles = map(int, roles) # convert to integers
        max_role = max(roles)
        max_role = max(max_role, 6) # max role should be at least 6

        ROLES_MAPPING[str(max_role)] = 'Authenticated'
        ROLES_MAPPING[str(max_role - 1)] = 'Anonymous'
        for i in xrange(5, max_role - 1):
            ROLES_MAPPING[str(i)] = 'Viewer'

    def get_role(circa_profile):
        DEFAULT_ROLE = 'Viewer'

        if circa_profile in ROLES_MAPPING:
            return ROLES_MAPPING[circa_profile]
        return DEFAULT_ROLE

    fd = open(filepath, 'rb')
    acls, not_matched = get_acl_mapping(fd)
    fd.close()

    report = StringIO()
    compute_roles_mapping(acls)
    for path, values in acls.items():
        try:
            ob = site.unrestrictedTraverse(path.strip('/'))
        except KeyError:
            print>>report, "Couldn't find object at path: %s" % path
            continue

        # add users acls
        userids = [val[:-6] for val in values if val.endswith('@circa')]
        non_userids = [val for val in values if not val.endswith('@circa')]
        for user_id in userids:
            user = auth_tool.get_user_with_userid(user_id)
            if user is None:
                print>>report, 'User not found: %s' % user_id
                continue
            #set_acl_for_user(ob, user)
            print>>report, '(Deactivated) Granted view on path %s for user %s' % (path, user_id)

        # add roles acls
        roles = [val[2:] for val in non_userids if val.startswith('__')]
        roles = list(set(map(get_role, roles)))
        if roles:
            #set_acl_for_roles(ob, roles)
            print>>report, '(Deactivated) Granted view on path %s for roles %s' % (path, roles)

        # not matched values
        nonvals = [val for val in non_userids if not val.startswith('__')]
        if nonvals:
            print>>report, 'Not matched user or profile for %s' % nonvals

    if not_matched:
        print>>report, 'Not matched rows (from the exported file): %s' % not_matched

    return report.getvalue()
