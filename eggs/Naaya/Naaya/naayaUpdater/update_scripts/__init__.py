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
# Andrei Laza, Eau de Web


#Python imports
import os
from cStringIO import StringIO

#Zope imports
import Acquisition
import transaction
from OFS.SimpleItem import Item
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Naaya imports

class UpdateScript(Item, Acquisition.Implicit):
    """ """
    update_id = 'UpdateScript'
    title = 'Main class for update scripts'
    meta_type = 'Naaya Update Script'

    manage_options = (
        {'label': 'Update', 'action': 'manage_update'},
    )

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_update')
    def manage_update(self, REQUEST):
        """ perform this update """
        report = ''
        if REQUEST.REQUEST_METHOD == 'POST':
            report_file = StringIO()

            dry_run = (REQUEST.form.get('action') != 'Run update')
            if dry_run:
                print>>report_file, '<h3>Dry-run</h3>'
            else:
                transaction.get().note('running update script "%s"' % self.title)

            for portal_path in REQUEST.form.get("portal_paths", []):
                portal = self.unrestrictedTraverse(portal_path)
                self._do_update_on_portal(portal, report_file, dry_run)

            report = report_file.getvalue()

        return self.update_template(REQUEST, report=report, form=REQUEST.form)

    security.declareProtected(view_management_screens, 'update_template')
    update_template = PageTemplateFile('zpt/update_template', globals())

    def index_html(self, REQUEST):
        """ redirect to manage_workspace """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_workspace')


def register_scripts(updater):
    for filename in os.listdir(os.path.dirname(__file__)):
        if not (filename.startswith('update_') and filename.endswith('.py')):
            continue
        objects = __import__(filename[:-3], globals(), None, ['*'])
        for key, obj in objects.__dict__.iteritems():
            if (isinstance(obj, type) and issubclass(obj, UpdateScript) and
                    obj not in (UpdateScript, )):
                updater.register_update_script(obj.update_id, obj)
