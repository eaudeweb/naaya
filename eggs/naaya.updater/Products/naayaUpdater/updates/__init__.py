#Python imports
import os
import logging
from cStringIO import StringIO
import traceback

#Zope imports
from DateTime import DateTime
import Acquisition
from OFS.SimpleItem import Item
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# this is for compatibility with older versions of Zope (< 2.9)
try:
    import transaction
    begin_transaction = transaction.begin
    get_transaction = transaction.get
except:
    begin_transaction = get_transaction().begin

#Naaya imports
from Products.ExtFile.ExtFile import ExtFile

from zope.interface import implements
from Products.naayaUpdater.interfaces import IUpdateScript

_PRIORITIES = ['CRITICAL', 'HIGH', 'LOW']
PRIORITY = dict([(_PRIORITIES[i], i) for i in range(len(_PRIORITIES))])

LOGS_FOLDERNAME = 'update_logs'

class UpdateScript(Item, Acquisition.Implicit):
    """ Update script
    """
    implements(IUpdateScript)

    title = 'Main class for update scripts'
    meta_type = 'Naaya Update Script'
    creation_date = 'Jan 01, 2000'
    authors = ['John Doe']
    priority = PRIORITY['LOW']
    description = ''

    manage_options = (
        {'label': 'Update', 'action': 'manage_update'},
    )

    security = ClassSecurityInfo()

    # default implementations
    security.declareProtected(view_management_screens, 'get_authors_string')
    def get_authors_string(self):
        if len(self.authors) == 0:
            return ''
        return reduce(lambda x, y: x + ', ' + y, self.authors)

    security.declareProtected(view_management_screens, 'get_priority_string')
    def get_priority_string(self):
        return _PRIORITIES[self.priority]

    # implemented only by the subclasses
    security.declarePrivate('_update')
    def _update(self, portal):
        raise NotImplementedError

    security.declarePrivate('_setup_logger')
    def _setup_logger(self):
        self.log_output = StringIO()

        handler = logging.StreamHandler(self.log_output)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(levelname)s][%(asctime)s]  %(message)s')
        handler.setFormatter(formatter)

        self.log = logging.getLogger('naayaUpdater.' + self.id)
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(handler)

    security.declarePrivate('_save_log')
    def _save_log(self, data):
        logs_folder = getattr(self, LOGS_FOLDERNAME)

        log_filename = '%s-%s' % (DateTime().strftime('%Y.%m.%d_%H.%M.%S'), self.id)

        begin_transaction()
        transaction = get_transaction()
        logs_folder._setObject(log_filename, ExtFile(log_filename, log_filename))
        ob = logs_folder._getOb(log_filename)
        ob.manage_upload(data, 'text/html;charset=utf-8')
        transaction.note('Saved log file for update "%s"' % self.title)
        transaction.commit()

    security.declareProtected(view_management_screens, 'update')
    def update(self, portal, do_dry_run):
        begin_transaction()
        transaction = get_transaction()
        try:
            success = self._update(portal)

            transaction.note('Update "%s" on Naaya site "%s"' %
                (self.id, portal.absolute_url(1)))

            if do_dry_run:
                transaction.abort()
            else:
                transaction.commit()

        except Exception, e:
            self.log.error('Update script failed - "%s"' % str(e))
            self.log.error(traceback.format_exc())
            transaction.abort()
            success = False

        log_data = self.log_output.getvalue()
        return success, log_data

    security.declareProtected(view_management_screens, 'manage_update')
    def manage_update(self, REQUEST):
        """ perform this update """
        report = ''
        if REQUEST.REQUEST_METHOD == 'POST':
            self._setup_logger()

            do_dry_run = (REQUEST.form.get('action') != 'Run update')
            for portal_path in REQUEST.form.get("portal_paths", []):
                portal = self.unrestrictedTraverse(portal_path)
                success, log_data = self.update(portal, do_dry_run)

                report += '<br/><br/>'
                report += '<h4>'+portal_path+'</h4>'
                if success:
                    report += '<h4>SUCCESS</h4>'
                else:
                    report += '<h4>FAILED</h4>'
                report += html_quote(log_data)

            if not do_dry_run:
                self._save_log('<pre>%s</pre>' % report)

        return self.update_template(REQUEST, report=report, form=REQUEST.form)

    security.declareProtected(view_management_screens, 'update_template')
    update_template = PageTemplateFile('zpt/update_template', globals())

    def index_html(self, REQUEST):
        """ redirect to manage_workspace """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_workspace')

def html_quote(v):
    return v.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
