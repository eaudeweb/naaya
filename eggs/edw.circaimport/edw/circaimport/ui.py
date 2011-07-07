import os.path

from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from edw.circaimport import (work_in_zope, add_roles_from_circa_export,
                             add_notifications_from_circa_export,
                             add_acls_from_circa_export)

upload_prefix = None

import_all_zpt = PageTemplateFile('import_all.zpt', globals())
import_files_zpt = PageTemplateFile('import_files.zpt', globals())
import_files_result_zpt = PageTemplateFile('import_files_result.zpt', globals())
import_roles_zpt = PageTemplateFile('import_roles.zpt', globals())
import_notifications_zpt = PageTemplateFile('import_notifications.zpt',
                                        globals())
import_acls_zpt = PageTemplateFile('import_acls.zpt', globals())

class ImportAllFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"
        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_all_zpt.__of__(ctx)()

        reports = []

        filename_files = self.request.form['filename_files']
        import_files_path = self.request.form['import_files_path']
        if filename_files and import_files_path:
            files_ctx = ctx.restrictedTraverse(import_files_path)
            reports.append(work_in_zope(files_ctx, filename_files, upload_prefix))

        filename_roles = self.request.form['filename_roles']
        ldap_source_title = self.request.form['source_title']
        if filename_roles and ldap_source_title:
            reports.append(add_roles_from_circa_export(ctx, os.path.join(upload_prefix, filename_roles), ldap_source_title))

        filename_notifications = self.request.form['filename_notifications']
        if filename_notifications:
            reports.append(add_notifications_from_circa_export(ctx, os.path.join(upload_prefix, filename_notifications)))

        filename_acls = self.request.form['filename_acls']
        if filename_acls:
            reports.append(add_acls_from_circa_export(ctx, os.path.join(upload_prefix, filename_acls)))

        return import_all_zpt.__of__(ctx)(reports=reports)


class ImportFilesFromCirca_html(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        return import_files_zpt.__of__(ctx)()

class ImportFilesFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"
        ctx = self.context.aq_inner # because self subclasses from Explicit
        #name = ctx.REQUEST.get('name')
        name = self.request.form['filename']
        report = work_in_zope(ctx, name, upload_prefix)
        return import_files_result_zpt.__of__(ctx)(report=report)


class ImportRolesFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_roles_zpt.__of__(ctx)()

        name = self.request.form['filename']
        ldap_source_title = self.request.form['source_title']

        report = add_roles_from_circa_export(ctx, os.path.join(upload_prefix, name), ldap_source_title)

        return import_roles_zpt.__of__(ctx)(report=report)


class ImportNotificationsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_notifications_zpt.__of__(ctx)()

        name = self.request.form['filename']

        report = add_notifications_from_circa_export(ctx, os.path.join(upload_prefix, name))

        return import_notifications_zpt.__of__(ctx)(report=report)


class ImportACLsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_acls_zpt.__of__(ctx)()

        name = self.request.form['filename']

        report = add_acls_from_circa_export(ctx, os.path.join(upload_prefix, name))

        return import_acls_zpt.__of__(ctx)(report=report)
