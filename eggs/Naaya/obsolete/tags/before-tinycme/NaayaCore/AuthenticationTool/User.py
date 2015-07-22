# Copyright (c) 2001 New Information Paradigms Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
#
# $Id: User.py 1484 2004-04-16 11:00:57Z finrocvs $

from string import find
import time

from AccessControl.User import SimpleUser
from Globals import Persistent

class User(SimpleUser, Persistent):
    """ """

    # we don't want to support the domains thing
    domains = ()

    def __init__(self, name, password, roles, domains, firstname, lastname, email):
        # bypass immutability
        self.__ = password
        self.name = name
        self.roles = roles
        self.domains = domains
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.history = ''
        self.created = time.strftime('%d %b %Y %H:%M:%S')
        self.lastupdated = ''

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
        try:
            if find(self.REQUEST.HTTP_REFERER, 'login_html') != -1:
                self.history = time.strftime('%d %b %Y %H:%M:%S')
        except:
            pass
        return self.name

