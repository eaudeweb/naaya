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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Add last login and last post attributes to users"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update LDAP users properties'
        self.description = 'Add name and group details for users missing them'
        self.update_meta_type = ''

    def _verify_doc(self, doc):
        #unused
        pass

    def _list_updates(self):
        #unused
        pass

    def _update(self):
        z_root = self.unrestrictedTraverse('/', None)
        ldap_folder = getattr(z_root, 'acl_users')
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()

        for portal in portals:
            acl = portal.getAuthenticationTool()
            for source in acl.getSources():
                users = source.getUsersRoles(acl).keys()
                for user in users:
                    if source.getUserCanonicalName(user) == '-':
                        user_name = source.getUserFullName(user, ldap_folder)
                        source.setUserCanonicalName(user, user_name)
                        source.setUserLocation(user, 'Users')
                        logger.debug('Location: %s - user: %s', source.absolute_url(), user)

def register(uid):
    return CustomContentUpdater(uid)
