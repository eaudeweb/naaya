from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view
from AccessControl.Permission import Permission

from naaya.core.zope2util import relative_object_path

upload_prefix = None

import_zpt = PageTemplateFile('import.zpt', globals())
import_result_zpt = PageTemplateFile('import_result.zpt', globals())
import_roles_zpt = PageTemplateFile('import_roles.zpt', globals())
import_notifications_zpt = PageTemplateFile('import_notifications.zpt',
                                            globals())
import_acls_zpt = PageTemplateFile('import_acls.zpt', globals())

class ImportFromCirca_html(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        return import_zpt.__of__(ctx)()

class ImportFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"
        ctx = self.context.aq_inner # because self subclasses from Explicit
        from edw.circaimport import work_in_zope
        #name = ctx.REQUEST.get('name')
        name = self.request.form['filename']
        report = work_in_zope(ctx, name, upload_prefix)
        return import_result_zpt.__of__(ctx)(report=report)


class ImportRolesFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_roles_zpt.__of__(ctx)()

        from ldif_extract import get_user_and_group_mapping
        name = self.request.form['filename']
        ldap_source_title = self.request.form['source_title']
        user_2_role, group_2_role = get_user_and_group_mapping(
                                                upload_prefix + '/' + name)

        auth_tool = ctx.getAuthenticationTool()
        for source in auth_tool.getSources():
            if source.title == ldap_source_title:
                ldap_source = source
                break
        else:
            report = 'No user source named %s' % ldap_source_title
            return import_roles_zpt.__of__(ctx)(report=report)

        for userid, role in user_2_role.items():
            ldap_source.addUserRoles(userid, [role])

        for groupid, role in group_2_role.items():
            ldap_source.map_group_to_role(groupid, [role])

        return import_roles_zpt.__of__(ctx)(user_2_role=user_2_role,
                                            group_2_role=group_2_role)


class ImportNotificationsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_notifications_zpt.__of__(ctx)()

        from csv_extract import get_notifications_mapping
        name = self.request.form['filename']

        dbfile = open(upload_prefix + '/' + name, 'rb')
        notifications, not_matched = get_notifications_mapping(dbfile)
        dbfile.close()

        subscriptions = []
        errors = []
        ignored = {}
        notif_tool = ctx.getNotificationTool()
        auth_tool = ctx.getAuthenticationTool()
        for user_id, values in notifications.items():
            user = auth_tool.get_user_with_userid(user_id)
            if user is None:
                errors.append('User not found: %s' % user_id)
                continue

            for val in values:
                if val['notif_type'] == 3:
                    if user_id not in ignored:
                        ignored[user_id] = []
                    ignored[user_id].append(val['path'])
                    continue

                try:
                    ob = ctx.getSite().unrestrictedTraverse(val['path'].strip('/'))
                except KeyError:
                    errors.append("Couldn't find object at path: %s" % val['path'])
                    continue

                location = relative_object_path(ob, ctx.getSite())
                try:
                    notif_tool.add_account_subscription(user_id,
                                                        location,
                                                        'instant', 'en')
                except ValueError, msg:
                    errors.append(msg)
                    continue

                subscriptions.append({'user_id': user_id,
                                      'path': val['path']})

        return import_notifications_zpt.__of__(ctx)(subscriptions=subscriptions,
                                                    not_matched=not_matched,
                                                    ignored=ignored,
                                                    errors=errors)


class ImportACLsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_acls_zpt.__of__(ctx)()

        auth_tool = ctx.getAuthenticationTool()
        def set_acl_for_user(ob, user):
            ldap_source_title = auth_tool.getUserSource(user)
            location = relative_object_path(ob, ctx.getSite())
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

        def get_role(circa_profile):
            ROLES_MAPPING = {} # waiting for feedback on this
            DEFAULT_ROLE = 'Viewer'

            if circa_profile in ROLES_MAPPING:
                return ROLES_MAPPING[circa_profile]
            return DEFAULT_ROLE

        from acl_extract import get_acl_mapping
        name = self.request.form['filename']

        fd = open(upload_prefix + '/' + name, 'rb')
        acls, not_matched = get_acl_mapping(fd)
        fd.close()

        users_map, roles_map = {}, {}
        errors = []
        for path, values in acls.items():
            try:
                ob = ctx.getSite().unrestrictedTraverse(path.strip('/'))
            except KeyError:
                errors.append("Couldn't find object at path: %s" % path)
                continue

            # add users acls
            userids = [val[:-6] for val in values if val.endswith('@circa')]
            non_userids = [val for val in values if not val.endswith('@circa')]
            for user_id in userids:
                user = auth_tool.get_user_with_userid(user_id)
                if user is None:
                    errors.append('User not found: %s' % user_id)
                    continue
                set_acl_for_user(ob, user)
                if path not in users_map:
                    users_map[path] = []
                users_map[path].append(user_id)

            # add roles acls
            roles = [val[2:] for val in non_userids if val.startswith('__')]
            roles = list(set(map(get_role, roles)))
            if roles:
                set_acl_for_roles(ob, roles)
                roles_map[path] = roles

            # not matched values
            nonvals = [val for val in non_userids if not val.startswith('__')]
            if nonvals:
                errors.append('Not matched user or profile for %s' % nonvals)

        return import_acls_zpt.__of__(ctx)(users_map=users_map,
                                            roles_map=roles_map,
                                            errors=errors,
                                            not_matched=not_matched)
