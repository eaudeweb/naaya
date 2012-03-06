from StringIO import StringIO
from zipfile import ZipFile
import logging
import datetime

import backupdata

from naaya.core.zope2util import relative_object_path

logger = logging.getLogger('edw.circaimport.ui')

def add_files_and_folders_from_circa_export(context, name, root_path):
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
    logger.debug('start importing files and folders')

    from actors import ZopeActor
    assert '/' not in name and name != '..'
    zip_path = root_path + '/' + name
    zip_fs_file = open(zip_path, 'rb')

    zf = ZipFile(zip_fs_file)
    index_file = StringIO(zf.read('index.txt'))
    current_user = context.REQUEST.AUTHENTICATED_USER.getId()

    actor = ZopeActor(context, current_user)
    def _open_on_key_error(name):
        """
        Patches for when the names are wrong (usually unicode encoding problems)
        """
        chain = name.split('/')
        parent_path = '/'.join(chain[:-1])
        matching_path = parent_path + '/' + chain[-1][0]
        matches = [fname for fname in zf.namelist()
                if fname.startswith(matching_path)]
        assert len(matches) == 1
        return StringIO(zf.read(matches[0]))

    def open_backup_file(name):
        try:
            return StringIO(zf.read(name))
        except KeyError:
            return _open_on_key_error(name)

    def get_date(name):
        info = zf.getinfo(name)
        return datetime.date(*info.date_time[0:3])

    backupdata.walk_backup(index_file, open_backup_file, get_date, actor)

    actor.finished()

    zip_fs_file.close()

    logger.debug('done importing files and folders')

def get_acl_users_sources_titles(site):
    auth_tool = site.getAuthenticationTool()
    return [source.title for source in auth_tool.getSources()]

def add_roles_from_circa_export(site, filepath, ldap_source_title):
    logger.debug('start importing roles')

    from ldif_extract import get_user_and_group_mapping
    user_2_role, group_2_role = get_user_and_group_mapping(filepath)

    auth_tool = site.getAuthenticationTool()
    for source in auth_tool.getSources():
        if source.title == ldap_source_title:
            ldap_source = source
            break
    else:
        logger.error('No user source named %s', ldap_source_title)
        return

    for userid, role in user_2_role.items():
        if not ldap_source.has_user(userid):
            logger.error('No user named %s in source %s', userid, ldap_source_title)
            continue

        try:
            ldap_source.addUserRoles(userid, [role])
        except Exception, e:
            logger.error("Couldn't add role %s for user %s: %s", role, userid, e)
        else:
            logger.info('Added role %s for user %s', role, userid)

    for groupid, role in group_2_role.items():
        try:
            ldap_source.map_group_to_role(groupid, [role])
        except Exception, e:
            logger.error("Couldn't add role %s for group %s: %s", role, groupid, e)
        else:
            logger.info('Added role %s for group %s', role, groupid)

    logger.debug('done importing roles')

def add_notifications_from_circa_export(site, filepath, notif_type):
    logger.debug('start importing notifications')

    from notifications_extract import get_notifications_mapping
    dbfile = open(filepath, 'rb')
    notifications, not_matched = get_notifications_mapping(dbfile)
    dbfile.close()

    notif_tool = site.getNotificationTool()
    auth_tool = site.getAuthenticationTool()
    for user_id, values in notifications.items():
        user = auth_tool.get_user_with_userid(user_id)
        if user is None:
            logger.error('User not found: %s', user_id)
            continue

        for val in values:
            if val['notif_type'] == 3:
                logger.info('Ignoring (turned off) subscription for user %s at location %s', user_id, val['path'])
                continue

            val['path'] = val['path'].strip('/')
            if val['path'] not in ('', '/'):
                val['path'] = "library/%s" % val['path']
            try:
                ob = site.unrestrictedTraverse(val['path'])
            except KeyError:
                logger.error("Couldn't find object at path: %s", val['path'])
                continue

            location = relative_object_path(ob, site)
            try:
                notif_tool.add_account_subscription(user_id,
                                                    location,
                                                    notif_type, 'en')
            except ValueError, msg:
                logger.error("Couldn't add subscription for user %s at location %s: %s", user_id, val['path'], msg)
                continue

            logger.info('Added subscription for user %s at location %s', user_id, val['path'])

    logger.debug('done importing notifications')

def add_acls_from_circa_export(site, filepath):
    logger.debug('start importing acls')

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

    if not acls:
        logger.info('No matched acls')
        if not_matched:
            logger.warn('Not matched rows (from the exported file): %s' % not_matched)
        return

    compute_roles_mapping(acls)
    for path, values in acls.items():
        path = path.strip('/')
        if path not in ('', '/'):
            path = "library/%s" % path
        try:
            ob = site.unrestrictedTraverse(path)
        except KeyError:
            logger.error("Couldn't find object at path: %s", path)
            continue

        if ob.meta_type != 'Naaya Folder':
            logger.error("Object %r is not a folder (Naaya can only restrict permissions on folders)", relative_object_path(ob, site))
            continue

        # add users acls
        userids = [val[:-6] for val in values if val.endswith('@circa')]
        non_userids = [val for val in values if not val.endswith('@circa')]
        for user_id in userids:
            user = auth_tool.get_user_with_userid(user_id)
            if user is None:
                logger.error('User not found: %s', user_id)
                continue
            #set_acl_for_user(ob, user)
            logger.warn('(Deactivated) Granted view on path %s for user %s', path, user_id)

        # add roles acls
        roles = [val[2:] for val in non_userids if val.startswith('__')]
        roles = list(set(map(get_role, roles)))
        if roles:
            #set_acl_for_roles(ob, roles)
            logger.warn('(Deactivated) Granted view on path %s for roles %s', path, roles)

        # not matched values
        nonvals = [val for val in non_userids if not val.startswith('__')]
        if nonvals:
            logger.warn('Not matched user or profile for %s' % nonvals)

    if not_matched:
        logger.warn('Not matched rows (from the exported file): %s' % not_matched)

    logger.debug('done importing acls')
