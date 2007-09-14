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

# Zope imports
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class NaayaContentUpdater(Folder):
    """ Naaya Content Updater abstract class. Subclass it for your content.
    """
    meta_type = 'Naaya Content Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'
    security = ClassSecurityInfo()
    
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
        self.report = ''
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
    def _list_updates(self):
        """ Return all objects that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        updates = []
        for portal in portals:
            updates.extend(self._list_portal_updates(portal))
        return updates
    
    def _list_portal_updates(self, portal):
        """ Return all portal objects that need update"""
        docs = portal.getCatalogedObjects(meta_type=self.update_meta_type)
        updates = []
        for doc in docs:
            doc = self._verify_doc(doc)
            if not doc:
                continue
            updates.append(doc)
        return updates
    #
    # Public methods. 
    #
    security.declareProtected(view_management_screens, 'update')
    def update(self, REQUEST=None):
        """ Update site content. If safe is True nothing will be touched.
        """
        self.last_run = DateTime()
        self.report = self._update()
        if REQUEST:
            REQUEST.RESPONSE.redirect('index_html')
            
    security.declareProtected(view_management_screens, 'update')
    def list_updates(self):
        """ Return the list of updates that will have place.
        """
        return self._list_updates()

InitializeClass(NaayaContentUpdater)
