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
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Cornel Nitu - Finsiel Romania

from string import find
import time

from AccessControl.User import SimpleUser
from Globals import Persistent

class User(SimpleUser, Persistent):
    """ """

    # we don't want to support the domains thing
    domains = ()

    def __init__(self, name, password, roles, firstname, lastname, email):
        # bypass immutability
        self.__ = password
        self.name = name
        self.roles = roles
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.history = ''
        self.created = time.strftime('%d %b %Y %H:%M:%S')
        self.lastupdated = ''
        self.notifications = []

    def _getPassword(self):
        """Return the password of the user."""
        return self.__

    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        # This is always an empty tuple, since we don't support
        # domain restrictions.
        return ()

    def getRoles(self):
        """Return the list of roles assigned to a user."""
        if self.name == 'Anonymous User': return tuple(self.roles)
        else: return tuple(self.roles) + ('Authenticated',)

    def getUserName(self):
        """Return the username of a user"""
        return self.name