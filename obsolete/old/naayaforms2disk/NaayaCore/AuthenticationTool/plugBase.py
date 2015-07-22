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
# The Original Code is Naaya version 1.0
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
#
#
#
#$Id: plugBase.py 2563 2004-11-12 11:44:47Z finrocvs $

#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass

#Product imports
from Products.NaayaCore.constants import *

class PlugBase(SimpleItem):
    """ """

    manage_options = (
        SimpleItem.manage_options
        )

    def __init__(self):
        """ """
        self.id = None
        self.obj_path = None
        self.title = None

    def getUserFolder(self):
        #return the user folder object
        l_obj = self.unrestrictedTraverse('/' + self.obj_path, None)
        if l_obj is None: return None
        else: return l_obj

    def getLocalRoles(self, p_local_roles):
        #returns a list of local roles
        l_temp = []
        for l_role in list(p_local_roles):
            if l_role not in ['Owner', 'Authenticated']: l_temp.append(l_role)
        return l_temp

    def getUsersRoles(self, p_user_folder, p_meta_types=None):
        #returns a structure with user roles by objects
        if p_meta_types is None: p_meta_types = self.get_containers_metatypes()
        l_users_roles = {}
        l_folders = self.getCatalogedObjects(meta_type=p_meta_types, has_local_role=1)
        l_folders.append(self.getSite())
        for l_item in l_folders:
            for l_roles_tuple in l_item.get_local_roles():
                l_local_roles = self.getLocalRoles(l_roles_tuple[1])
                user = l_roles_tuple[0]
                if self.getUserSource(user) != 'acl_users' and len(l_local_roles)>0:
                    if l_users_roles.has_key(str(user)):
                        l_users_roles[str(user)].append((l_local_roles, l_item.absolute_url(1)))
                    else:
                        l_users_roles[str(user)] = [(l_local_roles, l_item.absolute_url(1))]
        return l_users_roles

    def revokeUserRoles(self, roles='', REQUEST=None):
        """ """
        #process form values
        if roles == '': roles = []
        else: roles = self.utConvertToList(roles)
        for l_role in roles:
            l_users_roles = l_role.split('||')
            if not l_users_roles[1] and getattr(self, 'getSite', None):
                l_users_roles[1] = self.getSite().getId()
            l_user = self.utConvertToList(l_users_roles[0])
            l_location = self.utGetObject(l_users_roles[1])
            l_location.manage_delLocalRoles(l_user)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def addUserRoles(self, name='', roles='', loc='allsite', location='', user_location='', REQUEST=None):
        """ """
        site = self.getSite()
        auth_tool = site.getAuthenticationTool()
        #process form values
        if name == '':  name = []
        else: name = self.utConvertToList(name)
        if loc == 'allsite': location = site
        else: location = self.utGetObject(location)
        if roles == '': roles = []
        else: roles = self.utConvertToList(roles)
        #assing roles
        for n in name:
            location.manage_setLocalRoles(n, roles)
            try:
                email = auth_tool.getUsersEmails([n])[0]
                fullname = auth_tool.getUsersFullNames([n])[0]
                site.sendAccountCreatedEmail(fullname, email, n, REQUEST)
            except:
                pass
            try:
                self.setUserLocation(n, user_location)
                self.setUserCanonicalName(n, self.buffer[n])
            except:
                pass
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

InitializeClass(PlugBase)
