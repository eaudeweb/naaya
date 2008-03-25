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
# Alin Voinea, Eau de Web

#Python imports
import os

# Zope imports
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ExtFile.ExtFile import ExtFile
from Products.naayaUpdater.updates import LOG_ROOT, LOG_FILE

class NaayaContentUpdater(Folder):
    """ Naaya Content Updater abstract class. Subclass it for your content.
    """
    meta_type = 'Naaya Content Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'
    security = ClassSecurityInfo()
    bulk_update = True
    
    def manage_options(self):
        """ ZMI tabs """
        return ({'label': 'Update', 'action': 'index_html'},)
    ###
    #General stuff
    ######
    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('updates/zpt/content_updater_index', globals())

    def __init__(self, id):
        self.id = id
        self.title = 'Naaya Content Updater'
        self.description = ''
        self.update_meta_type = ''
        self.last_run = None
    #
    # Methods to override
    #
    def _update(self):
        """ Do update"""
        #'Implement it for your content type.
        return "NotImplementedError"
    
    def _verify_doc(self, doc):
        """ Return None if doc doesn't need updates, doc otherrwise."""
        #'Implement it for your content type.
        return doc
    #
    # Util methods
    #
    def _reset_log(self, backup=''):
        """ Remove log file """
        if backup:
            f = open(LOG_FILE, 'r')
            data = f.read()
            f.close()
            f = open(backup, 'w')
            f.write(data)
            f.close()
        open(LOG_FILE, 'w').close()
        
    def _list_updates(self):
        """ Return all objects that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            query = {'meta_type': portal.utConvertToList(self.update_meta_type)}
            brains = portal.getCatalogTool()(query)
            for brain in brains:
                doc = brain.getObject()
                if doc is None:
                    continue
                if not self._verify_doc(doc):
                    continue
                yield doc
    #
    # Public methods. 
    #
    security.declarePrivate('add_report')
    def add_report(self):
        """ Add update report """
        if not os.path.isfile(LOG_FILE):
            return
        log = open(LOG_FILE, 'rb')
        data = log.read()
        log.close()
        if not data:
            return
        time = DateTime()
        report_id = 'update_' + time.strftime('%Y-%m-%d-%H-%M-%S') + '.log'
        report_title = 'Update on %s' % time
        tmpExtFile = ExtFile(report_id, report_title)
        self._setObject(report_id, tmpExtFile)
        self._getOb(report_id).manage_upload(data, 'text/plain')
        self._reset_log(backup=os.path.join(LOG_ROOT, report_id))
        
    security.declareProtected(view_management_screens, 'update')
    def update(self, REQUEST=None):
        """ Update site content. If safe is True nothing will be touched.
        """
        self._reset_log()
        self._update()
        self.add_report()
        self.last_run = DateTime()
        if REQUEST:
            REQUEST.RESPONSE.redirect('index_html')
            
    security.declareProtected(view_management_screens, 'list_updates')
    def list_updates(self):
        """ Return the list of updates that will have place.
        """
        return self._list_updates()

InitializeClass(NaayaContentUpdater)
