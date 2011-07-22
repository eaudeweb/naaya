import os.path
import logging
import traceback
from StringIO import StringIO

from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import transaction

from middleware import (add_files_and_folders_from_circa_export,
                             get_acl_users_sources_titles,
                             add_roles_from_circa_export,
                             add_notifications_from_circa_export,
                             add_acls_from_circa_export)

upload_prefix = None
logger = logging.getLogger('edw.circaimport.ui')
logger.setLevel(logging.DEBUG)

import_all_zpt = PageTemplateFile('zpt/import_all.zpt', globals())
import_files_zpt = PageTemplateFile('zpt/import_files.zpt', globals())
import_files_result_zpt = PageTemplateFile('zpt/import_files_result.zpt',
                                        globals())
import_roles_zpt = PageTemplateFile('zpt/import_roles.zpt', globals())
import_notifications_zpt = PageTemplateFile('zpt/import_notifications.zpt',
                                        globals())
import_acls_zpt = PageTemplateFile('zpt/import_acls.zpt', globals())

def init_log_stream():
    log = StringIO()
    handler = logging.StreamHandler(log)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(UIFormatter())
    logger.addHandler(handler)
    return log

class UIFormatter(logging.Formatter):
    color_codes = {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'orange',
            'ERROR': 'orangered',
            'CRITICAL': 'red'
            }
    html = """<span style="color: %s">%s: %s</span>"""
    def format(self, record):
        message = record.msg % record.args
        return self.html % (self.color_codes[record.levelname],
                            record.levelname,
                            message)

class ImportAllFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"
        ctx = self.context.aq_inner # because self subclasses from Explicit
        sources = get_acl_users_sources_titles(ctx)
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_all_zpt.__of__(ctx)(sources=sources)

        log = init_log_stream()
        try:
            if 'report' in self.request.form:
                savepoint = transaction.savepoint()

            filename_files = self.request.form['filename_files']
            import_files_path = self.request.form['import_files_path']
            if filename_files and import_files_path:
                try:
                    files_ctx = ctx.restrictedTraverse(import_files_path)
                    add_files_and_folders_from_circa_export(files_ctx, filename_files, upload_prefix)
                except:
                    logger.critical(traceback.format_exc())

            filename_roles = self.request.form['filename_roles']
            ldap_source_title = self.request.form['source_title']
            if filename_roles and ldap_source_title:
                try:
                    add_roles_from_circa_export(ctx, os.path.join(upload_prefix, filename_roles), ldap_source_title)
                except:
                    logger.critical(traceback.format_exc())

            filename_notifications = self.request.form['filename_notifications']
            if filename_notifications:
                try:
                    add_notifications_from_circa_export(ctx, os.path.join(upload_prefix, filename_notifications))
                except:
                    logger.critical(traceback.format_exc())

            filename_acls = self.request.form['filename_acls']
            if filename_acls:
                try:
                    add_acls_from_circa_export(ctx, os.path.join(upload_prefix, filename_acls))
                except:
                    logger.critical(traceback.format_exc())

        finally:
            if 'report' in self.request.form:
                savepoint.rollback()

        return import_all_zpt.__of__(ctx)(sources=sources, report=log.getvalue())


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

        log = init_log_stream()

        try:
            add_files_and_folders_from_circa_export(ctx, name, upload_prefix)
        except:
            logger.critical(traceback.format_exc())

        return import_files_result_zpt.__of__(ctx)(report=log.getvalue())


class ImportRolesFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        sources = get_acl_users_sources_titles(ctx)
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_roles_zpt.__of__(ctx)(sources=sources)

        name = self.request.form['filename']
        ldap_source_title = self.request.form['source_title']

        log = init_log_stream()

        try:
            add_roles_from_circa_export(ctx, os.path.join(upload_prefix, name), ldap_source_title)
        except:
            logger.critical(traceback.format_exc())

        return import_roles_zpt.__of__(ctx)(sources=sources, report=log.getvalue())


class ImportNotificationsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_notifications_zpt.__of__(ctx)()

        notif_type = self.request.form['notif_type']
        filename = self.request.form['filename']

        log = init_log_stream()

        try:
            add_notifications_from_circa_export(ctx,
                    os.path.join(upload_prefix, filename), notif_type)
        except:
            logger.critical(traceback.format_exc())

        return import_notifications_zpt.__of__(ctx)(report=log.getvalue())


class ImportACLsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_acls_zpt.__of__(ctx)()

        name = self.request.form['filename']

        log = init_log_stream()

        try:
            add_acls_from_circa_export(ctx, os.path.join(upload_prefix, name))
        except:
            logger.critical(traceback.format_exc())

        return import_acls_zpt.__of__(ctx)(report=log.getvalue())
