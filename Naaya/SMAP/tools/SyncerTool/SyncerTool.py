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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZSyncer.ZSyncer import ZSyncer

#Product imports
from Products.NaayaBase.constants import *
from Products.SMAP.tools.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaCore.managers.session_manager import session_manager

def manage_addSyncerTool(self, dest_server='', username='', password='', zope_syncable=[], ny_syncable=[], REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    ob = SyncerTool(ID_SYNCERTOOL, TITLE_SYNCERTOOL, dest_server, username, password, zope_syncable, ny_syncable)
    self._setObject(ID_SYNCERTOOL, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class SyncerTool(ZSyncer, utils, session_manager):
    """
    Class that implements the tool.
    """

    meta_type = METATYPE_SYNCERTOOL
    #icon = 'misc_/SMAP/SyncerTool.gif'

    manage_options = (
            {'label': 'Properties', 'action': 'manage_properties_html'},
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, dest_server, username, password, zope_syncable, ny_syncable):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        self.dest_server = dest_server
        self.username = username
        self.password = password
        self.zope_syncable = zope_syncable
        self.ny_syncable = ny_syncable
        ZSyncer.__dict__['__init__'](self, id, title)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, dest_server='', username='', password='', zope_syncable=None, ny_syncable=None, REQUEST=None):
        """ """
        self.dest_server = dest_server
        self.username = username
        self.password = password
        if zope_syncable is None: self.zope_syncable = []
        else: self.zope_syncable = self.utConvertToList(zope_syncable)
        if ny_syncable is None: self.ny_syncable = []
        else: self.ny_syncable = self.utConvertToList(ny_syncable)
        #save the properties in ZSyncer instance
        full_domain = ''
        if self.dest_server and self.username and self.password:
            dest_server = self.dest_server.replace('http://', '')
            full_domain = 'http://%s:%s@%s' % (self.username, self.password, dest_server)
        self.manage_editProperties({'title':self.title, 'dest_servers':full_domain, 'connection_type':'ConnectionMgr', 'use_relative_paths':1, \
                                    'filterObjects':1, 'syncable':self.zope_syncable, 'add_syncable':self.ny_syncable})
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'pushToRemote')
    def pushToRemote(self, folder='', REQUEST=None):
        """ Push each folder to destination server. """
        if folder:
            object_paths = self.utConvertToList(folder)
            msgs = self.manage_pushToRemote(object_paths, msgs=None)
            msg = msgs[0] #take the first message, because only one folder is syncronize
            if msg.status == 200:
                self.setSessionInfo([MSG_SYNCER_SUCCESS])
            else:
                self.setSessionErrors([MSG_SYNCER_FAILED])
        else:
            self.setSessionErrors([MSG_SYNCER_FAILED])
        if REQUEST:
            REQUEST.RESPONSE.redirect('commit_html?url=%s' % folder)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/syncer_properties', globals())

InitializeClass(SyncerTool)
