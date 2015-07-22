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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *

def manage_addNotificationTool(self, REQUEST=None):
    """ """
    ob = NotificationTool(ID_NOTIFICATIONTOOL, TITLE_NOTIFICATIONTOOL)
    self._setObject(ID_NOTIFICATIONTOOL, ob)
    self._getOb(ID_NOTIFICATIONTOOL).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NotificationTool(Folder):
    """ """

    meta_type = METATYPE_NOTIFICATIONTOOL
    icon = 'misc_/NaayaCore/NotificationTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Settings', 'action': 'manage_settings_html'},
        )
        +
        Folder.manage_options[3:]
    )

    meta_types = (
        #{'name': METATYPE_EMAILTEMPLATE, 'action': 'manage_addEmailTemplateForm'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.newsmetatypes = []
        self.uploadmetatypes = []
        self.foldermetatypes = []
        self.subject_notifications=''
        self.subject_newsletter=''
        self.from_email=''
        self.monitorized_folders=[]

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

    #core
    security.declarePrivate('add_newsmetatype')
    def add_newsmetatype(self, m):
        """
        Add a new news meta types to list.
        @param l: object meta type
        @type l: string
        """
        if m not in self.newsmetatypes:
            self.newsmetatypes.append(m)
            self._p_changed = 1

    security.declarePrivate('del_newsmetatype')
    def del_newsmetatype(self, m):
        """
        Remove a news meta types from list.
        @param l: object meta type
        @type l: string
        """
        if m in self.newsmetatypes:
            self.newsmetatypes.remove(m)
            self._p_changed = 1

    security.declarePrivate('add_uploadmetatype')
    def add_uploadmetatype(self, m):
        """
        Add a new upload meta types to list.
        @param l: object meta type
        @type l: string
        """
        if m not in self.uploadmetatypes:
            self.uploadmetatypes.append(m)
            self._p_changed = 1

    security.declarePrivate('del_uploadmetatype')
    def del_uploadmetatype(self, m):
        """
        Remove a upload meta types from list.
        @param l: object meta type
        @type l: string
        """
        if m in self.uploadmetatypes:
            self.uploadmetatypes.remove(m)
            self._p_changed = 1

    security.declarePrivate('add_foldermetatype')
    def add_foldermetatype(self, m):
        """
        Add a new folder meta types to list.
        @param l: object meta type
        @type l: string
        """
        if m not in self.foldermetatypes:
            self.foldermetatypes.append(m)
            self._p_changed = 1

    security.declarePrivate('del_foldermetatype')
    def del_foldermetatype(self, m):
        """
        Remove a folder meta types from list.
        @param l: object meta type
        @type l: string
        """
        if m in self.foldermetatypes:
            self.foldermetatypes.remove(m)
            self._p_changed = 1

    security.declarePublic('get_monitorized_folders')
    def get_monitorized_folders(self):
        return self.monitorized_folders
    
    security.declarePrivate('add_monitorized_folder')
    def add_monitorized_folder(self, folder_path):
        self.monitorized_folders.append(folder_path)
        self._p_changed = 1
    
    security.declarePrivate('del_monitorized_folder')
    def del_monitorized_folder(self, folder_path):
        self.monitorized_folders.remove(folder_path)
        self._p_changed = 1

    security.declarePrivate('del_folders_from_notification_list')
    def del_folders_from_notification_list(self, folders_list=[]):
        if folders_list != []:
            for i in folders_list:
                self.del_monitorized_folder(i)

    security.declarePrivate('add_folders_to_notification_list')
    def add_folders_to_notification_list(self, folders_path_list=[]):
        if folders_path_list != []:
            for i in folders_path_list:
                try: self.add_monitorized_folder(i)
                except: pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manageSettings')
    def manageSettings(self, newsmetatypes='', uploadmetatypes='',
        foldermetatypes='', subject_notifications='', subject_newsletter='', from_email='', monitorized_folders=[], REQUEST=None):
        """ """
        newsmetatypes = self.utConvertLinesToList(newsmetatypes)
        uploadmetatypes = self.utConvertLinesToList(uploadmetatypes)
        foldermetatypes = self.utConvertLinesToList(foldermetatypes)
        #save data
        self.newsmetatypes = newsmetatypes
        self.uploadmetatypes = uploadmetatypes
        self.foldermetatypes = foldermetatypes
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_settings_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_settings_html')
    manage_settings_html = PageTemplateFile('zpt/notification_settings', globals())

    def set_email_credentials(self, from_email, subject_notifications='', subject_newsletter=''):
        """sets the subject of the newsletter, of the newsletter and of the sender in the lang language"""
        self.subject_notifications = subject_notifications
        self.subject_newsletter = subject_newsletter
        self.from_email = from_email
        self._p_changed = 1

InitializeClass(NotificationTool)
