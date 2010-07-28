# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


#Python imports
import traceback

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
# this is for compatibility with older versions of Zope (< 2.9)
try:
    import transaction
    begin_transaction = transaction.begin
    get_transaction = transaction.get
except:
    begin_transaction = get_transaction().begin


#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateRemoveObsoletes(UpdateScript):
    """ Removes obsolete objects from portal root """
    title = 'Remove obsolete object instances'
    creation_date = 'Aug 25, 2009'
    authors = ['David Batranu']
    description = 'Deletes obsolete object instances from portal root. Currently lists broken instances' #TODO: Extend to portal properties
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal, obsoletes):
        if obsoletes['broken']:
            portal.manage_delObjects(list(obsoletes['broken'])) #I give it a copy of the list since it clears it and there's nothing left to log
            self.log.debug('Deleted %s' % obsoletes['broken'])
        else:
            self.log.debug('Nothing to delete')
        return True

    def get_broken_objects(self, portal_path):
        broken = []
        portal = self.unrestrictedTraverse(portal_path)
        for oid in portal.objectIds():
            if portal[oid].meta_type == "Broken Because Product is Gone":
                broken.append(oid)
        return broken

    def get_obsoletes(self, REQUEST):
        obsoletes = {}
        for portal_path in REQUEST.form.get("portal_paths", []):
            if portal_path.startswith('/'):
                portal_path = portal_path[1:]
            obsoletes.setdefault(portal_path, {})['broken'] = self.get_broken_objects(portal_path)
        return obsoletes

    def manage_update(self, REQUEST):
        """ perform the update """
        action = REQUEST.form.get('action', '')
        report, obsoletes = "", {}
        if action and action != 'Show obsoletes':
            do_dry_run = (action == 'Show report')

            # get broken objects
            broken_objects = {}
            for path in REQUEST.form.get("broken", []):
                path = path.split('/')
                portal_path, bid = '/'.join(path[:-1]), path[-1]
                broken_objects.setdefault(portal_path, []).append(bid)

            obsoletes = {}
            # add broken objects to obsoletes
            for ppath, bobjs in broken_objects.items():
                obsoletes.setdefault(ppath, {})['broken'] = bobjs

            for portal_path, obs in obsoletes.items():
                portal = self.unrestrictedTraverse(portal_path)
                success, log_data = self.update(portal, obs, do_dry_run)

                report += '<br/><br/>'
                report += '<h4>'+portal_path+'</h4>'
                if success:
                    report += '<h4>SUCCESS</h4>'
                else:
                    report += '<h4>FAILED</h4>'
                report += log_data
        return self.update_template(REQUEST, obsoletes=obsoletes, report=report, form=REQUEST.form)

    security.declareProtected(view_management_screens, 'update')
    def update(self, portal, obsoletes, do_dry_run):
        self._setup_logger()

        begin_transaction()
        transaction = get_transaction()
        try:
            success = self._update(portal, obsoletes)

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
        self._save_log(log_data, portal)
        return success, log_data

    security.declareProtected(view_management_screens, 'standard_update_template')
    standard_update_template = PageTemplateFile('zpt/update_template', globals())

    security.declareProtected(view_management_screens, 'update_template')
    update_template = PageTemplateFile('zpt/update_remove_obsoletes', globals())

