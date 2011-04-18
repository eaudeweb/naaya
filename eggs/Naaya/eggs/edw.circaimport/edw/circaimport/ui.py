from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from naaya.core.zope2util import relative_object_path

upload_prefix = None

import_zpt = PageTemplateFile('import.zpt', globals())
import_result_zpt = PageTemplateFile('import_result.zpt', globals())
import_roles_zpt = PageTemplateFile('import_roles.zpt', globals())
import_notifications_zpt = PageTemplateFile('import_notifications.zpt',
                                            globals())

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
        notif_tool = ctx.getNotificationTool()
        auth_tool = ctx.getAuthenticationTool()
        for user_id, paths in notifications.items():
            user = auth_tool.get_user_with_userid(user_id)
            if user is None:
                errors.append('User not found: %s' % user_id)
                continue

            for path in paths:
                try:
                    ob = ctx.getSite().unrestrictedTraverse(path.strip('/'))
                except KeyError, msg:
                    errors.append("Couldn't find object at path: %s" % path)
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
                                      'path': path})

        return import_notifications_zpt.__of__(ctx)(subscriptions=subscriptions,
                                                    not_matched=not_matched,
                                                    errors=errors)
