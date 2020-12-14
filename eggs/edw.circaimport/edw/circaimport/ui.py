import os.path
import logging
import traceback
import operator
from StringIO import StringIO

from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import transaction

from Products.Naaya.constants import METATYPE_NYSITE
from naaya.groupware.constants import METATYPE_GROUPWARESITE

from edw.circaimport.middleware import add_files_and_folders_from_circa_export
from edw.circaimport.middleware import get_acl_users_sources_titles
from edw.circaimport.middleware import add_roles_from_circa_export
from edw.circaimport.middleware import add_notifications_from_circa_export
from edw.circaimport.middleware import add_acls_from_circa_export
from edw.circaimport import zexpcopy


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
zexpcopy_export_zpt = PageTemplateFile('zpt/zexpcopy/export.zpt', globals())
zexpcopy_import_zpt = PageTemplateFile('zpt/zexpcopy/import.zpt', globals())
zexpcopy_tree_ajax_zpt = PageTemplateFile('zpt/zexpcopy/tree_ajax.zpt',
                                          globals())
tpl_macros = PageTemplateFile('zpt/zexpcopy/macros.zpt', globals()).macros


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
        ctx = self.context.aq_inner  # because self subclasses from Explicit
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
                    add_files_and_folders_from_circa_export(
                        files_ctx, filename_files, upload_prefix)
                except Exception:
                    logger.critical(traceback.format_exc())

            filename_roles = self.request.form['filename_roles']
            ldap_source_title = self.request.form['source_title']
            if filename_roles and ldap_source_title:
                try:
                    add_roles_from_circa_export(
                        ctx, os.path.join(upload_prefix, filename_roles),
                        ldap_source_title)
                except Exception:
                    logger.critical(traceback.format_exc())

            filename_notifications = self.request.form.get(
                'filename_notifications')
            if filename_notifications:
                try:
                    add_notifications_from_circa_export(
                        ctx, os.path.join(upload_prefix,
                                          filename_notifications))
                except Exception:
                    logger.critical(traceback.format_exc())

            filename_acls = self.request.form['filename_acls']
            if filename_acls:
                try:
                    add_acls_from_circa_export(
                        ctx, os.path.join(upload_prefix, filename_acls))
                except Exception:
                    logger.critical(traceback.format_exc())

        finally:
            if 'report' in self.request.form:
                savepoint.rollback()

        return import_all_zpt.__of__(ctx)(sources=sources,
                                          report=log.getvalue())


class ImportFilesFromCirca_html(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner  # because self subclasses from Explicit
        return import_files_zpt.__of__(ctx)()


class ImportFilesFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"
        ctx = self.context.aq_inner  # because self subclasses from Explicit
        # name = ctx.REQUEST.get('name')
        name = self.request.form['filename']
        if not name:
            name = '%s.zip' % ctx.getSite().getId()

        log = init_log_stream()

        try:
            add_files_and_folders_from_circa_export(ctx, name, upload_prefix)
        except Exception:
            logger.critical(traceback.format_exc())

        return import_files_result_zpt.__of__(ctx)(report=log.getvalue())


class ImportRolesFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner  # because self subclasses from Explicit
        sources = get_acl_users_sources_titles(ctx)
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_roles_zpt.__of__(ctx)(sources=sources)

        name = self.request.form['filename']
        if not name:
            name = '%s.ldif' % ctx.getId()
        ldap_source_title = self.request.form['source_title']

        log = init_log_stream()

        try:
            add_roles_from_circa_export(
                ctx, os.path.join(upload_prefix, name), ldap_source_title)
        except Exception:
            logger.critical(traceback.format_exc())

        return import_roles_zpt.__of__(ctx)(sources=sources,
                                            report=log.getvalue())


class ImportNotificationsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner  # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_notifications_zpt.__of__(ctx)()

        notif_type = self.request.form['notif_type']
        filename = self.request.form['filename']
        if not filename:
            filename = '%s.library.usernotification.txt' % ctx.getId()

        log = init_log_stream()

        try:
            add_notifications_from_circa_export(
                ctx, os.path.join(upload_prefix, filename), notif_type)
        except Exception:
            logger.critical(traceback.format_exc())

        return import_notifications_zpt.__of__(ctx)(report=log.getvalue())


class ImportACLsFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"

        ctx = self.context.aq_inner  # because self subclasses from Explicit
        if self.request['REQUEST_METHOD'] == 'GET':
            return import_acls_zpt.__of__(ctx)()

        name = self.request.form['filename']
        if not name:
            name = '%s.itemsacls.txt' % ctx.getId()

        log = init_log_stream()

        try:
            add_acls_from_circa_export(ctx, os.path.join(upload_prefix, name))
        except Exception:
            logger.critical(traceback.format_exc())

        return import_acls_zpt.__of__(ctx)(report=log.getvalue())


class ZExportData(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner
        info = error = ''
        sites = ctx.objectValues([METATYPE_NYSITE, METATYPE_GROUPWARESITE])
        sites = [(s.getId(), s.title_or_id()) for s in sites]
        sites.sort(key=operator.itemgetter(0))
        submit = self.request.form.get('submit')
        if submit:
            path = self.request.form.get('location')
            ig_id = self.request.form.get('ig')
            ob = ctx.unrestrictedTraverse('/%s/%s' % (ig_id, path))
            sender = ctx.applications.mail_from
            user_id = self.request.AUTHENTICATED_USER.getId()
            user = ob.getAuthenticationTool().get_user_with_userid(user_id)
            to = user.mail
            try:
                zexp_path = zexpcopy.write_zexp(ob)
            except Exception as e:
                zexp_path = ''
                error = "Error while exporting %s IG Data: %s" % (ig_id,
                                                                  e.args)
                logger.exception(error)
                subject = 'Error exporting IG Data'
                zexpcopy.send_action_completed_mail(error, sender, to, subject)
            else:
                info = zexpcopy.export_completed_message_zpt.__of__(ctx)(
                    zexp_path=zexp_path, ob_url=ob.absolute_url())
                subject = 'IG Data exported successfully'
                zexpcopy.send_action_completed_mail(info, sender, to, subject)
            options = {
                'performed': True,
                'zexp_path': zexp_path,
                'info': info.replace('\n', '<br />\n'),
                'error': error,
                'igs': sites,
                'macros': tpl_macros,
            }
            return zexpcopy_export_zpt.__of__(ctx)(**options)
        else:
            return zexpcopy_export_zpt.__of__(ctx)(performed=False,
                                                   igs=sites,
                                                   macros=tpl_macros)


class ZImportData(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner
        info = error = ''
        sites = ctx.objectValues([METATYPE_NYSITE, METATYPE_GROUPWARESITE])
        sites = [(s.getId(), s.title_or_id()) for s in sites]
        sites.sort(key=operator.itemgetter(0))
        submit = self.request.form.get('submit')
        if submit:
            user_id = self.request.AUTHENTICATED_USER.getId()
            zexp_path = self.request.form.get('zexp_path')
            path = self.request.form.get('location')
            ig_id = self.request.form.get('ig')
            if not ig_id or ig_id == '-':
                ob = ctx.unrestrictedTraverse('/')
                user = ob.acl_users['ldap-plugin'].acl_users.getUser(user_id)
            else:
                ob = ctx.unrestrictedTraverse('/%s/%s' % (ig_id, path))
                user = ob.getAuthenticationTool().get_user_with_userid(user_id)
            sender = ctx.applications.mail_from

            to = user.mail
            new_ids = []
            sp = transaction.savepoint()
            try:
                new_ids = zexpcopy.load_zexp(zexp_path, ob)
            except IOError as e:
                sp.rollback()
                error = (('Can not read file with exported data. '
                          'Did you enter correctly the path you received by '
                          'email after export?. Error was: %s') % e.args)
                logger.exception(error)
            except Exception as e:
                sp.rollback()
                error = 'Error importing data from zexp file: %s' % e.args
                logger.exception(error)
                subject = 'Error importing IG Data'
                zexpcopy.send_action_completed_mail(error, sender, to, subject)
            else:
                if ob.meta_type == 'Groupware site':
                    imported_path = ob.absolute_url()
                else:
                    imported_path = ob.absolute_url() + '/' + new_ids[0]
                info = (('The import process ended without errors.'
                        ' Data was imported in this folder, please check: %s')
                        % imported_path)
                subject = 'IG Data imported successfully'
                zexpcopy.send_action_completed_mail(info, sender, to, subject)
            return zexpcopy_import_zpt.__of__(ctx)(performed=True, ob=ob,
                                                   new_ids=new_ids, info=info,
                                                   error=error, igs=sites,
                                                   macros=tpl_macros)
        else:
            return zexpcopy_import_zpt.__of__(ctx)(performed=False,
                                                   igs=sites,
                                                   macros=tpl_macros)


class ZExpcopyTree(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner
        site = ctx.unrestrictedTraverse(self.request.form.get('ig'))
        return zexpcopy_tree_ajax_zpt.__of__(ctx)(site=site)
