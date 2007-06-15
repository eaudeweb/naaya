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

#constants
_SESSION_ERRORS = "site_errors"
_SESSION_INFO = "site_infos"

class session_manager:
    """This class has some methods to work with session variables"""

    def __init__(self):
        """Constructor"""
        pass

    def __isSession(self, key):
        """Test if exists a variable with the given key in SESSION"""
        return self.REQUEST.SESSION.has_key(key)

    def __getSession(self, key, default):
        """Get a key value from SESSION; if that key doesn't exist then return default value"""
        try: return self.REQUEST.SESSION[key]
        except: return default

    def __setSession(self, key, value):
        """Add a value to SESSION"""
        try: self.REQUEST.SESSION.set(key, value)
        except: pass

    def __delSession(self, key):
        """Delete a value from SESSION"""
        try: self.REQUEST.SESSION.delete(key)
        except: pass

    #Public methods
    def getSession(self, key, default):
        """ Returns the session value for one key """
        return self.__getSession(key, default)
    def setSession(self, key, value):
        """ Set the session value for key """
        return self.__setSession(key, value)
    def delSession(self, key):
        """ Delete a key from session """
        return self.__delSession(key)
    def delSessionKeys(self, keys):
        """ Delete one or more keys from session """
        map(self.__delSession, keys)
    def isSession(self, key):
        """ Returns true if this key exists in session """
        return self.__isSession(key)

    #manage information
    def isSessionInfo(self):
        """Returns true if this key exists"""
        return self.__isSession(_SESSION_INFO)
    def getSessionInfo(self, default=None):
        """Returns the session value for errors"""
        return self.__getSession(_SESSION_INFO, default)
    def setSessionInfo(self, value):
        """Set the session value for errors"""
        self.__setSession(_SESSION_INFO, value)
    def delSessionInfo(self):
        """Delete a key"""
        self.__delSession(_SESSION_INFO)

    #manage errors
    def isSessionErrors(self):
        """Returns true if this key exists"""
        return self.__isSession(_SESSION_ERRORS)
    def getSessionErrors(self, default=None):
        """Returns the session value for errors"""
        return self.__getSession(_SESSION_ERRORS, default)
    def setSessionErrors(self, value):
        """Set the session value for errors"""
        self.__setSession(_SESSION_ERRORS, value)
    def delSessionErrors(self):
        """Delete a key"""
        self.__delSession(_SESSION_ERRORS)

    #manage users
    def setUserSession(self, name, roles, domains, firstname, lastname, email, password):
        """ put the user information on session """
        self.__setSession('user_name', name)
        self.__setSession('user_roles', roles)
        self.__setSession('user_domains', domains)  #not used for the moment
        self.__setSession('user_firstname', firstname)
        self.__setSession('user_lastname', lastname)
        self.__setSession('user_email', email)
        self.__setSession('user_password', password)

    def delUserSession(self):
        """ delete user information from session """
        self.__delSession('user_name')
        self.__delSession('user_roles')
        self.__delSession('user_domains')
        self.__delSession('user_firstname')
        self.__delSession('user_lastname')
        self.__delSession('user_email')
        self.__delSession('user_password')

    def setRequestRoleSession(self, name, firstname, lastname, email, password,
        organisation, comments, location):
        """ """
        self.setUserSession(name, '', '', firstname, lastname, email, password)
        self.__setSession('user_organisation', organisation)
        self.__setSession('user_comments', comments)
        self.__setSession('user_location', location)

    def delRequestRoleSession(self):
        """ """
        self.delUserSession()
        self.__delSession('user_organisation')
        self.__delSession('user_comments')
        self.__delSession('user_location')

    def setCreateAccountSession(self, name, firstname, lastname, email, password):
        """ """
        self.setUserSession(name, '', '', firstname, lastname, email, password)

    def delCreateAccountSession(self):
        """ """
        self.delUserSession()

    def getSessionUserName(self, default=''):
        return self.__getSession('user_name', default)

    def getSessionUserRoles(self, default=''):
        return self.__getSession('user_roles', default)

    def getSessionUserDomains(self, default=''):
        return self.__getSession('user_domains', default)

    def getSessionUserFirstname(self, default=''):
        return self.__getSession('user_firstname', default)

    def getSessionUserLastname(self, default=''):
        return self.__getSession('user_lastname', default)

    def getSessionUserEmail(self, default=''):
        return self.__getSession('user_email', default)

    def getSessionUserPassword(self, default=''):
        return self.__getSession('user_password', default)

    def getSessionUserOrganisation(self, default=''):
        return self.__getSession('user_organisation', default)

    def getSessionUserComments(self, default=''):
        return self.__getSession('user_comments', default)

    def getSessionUserLocation(self, default=''):
        return self.__getSession('user_location', default)

    #feedback session
    def setFeedbackSession(self, name='', email='', comments='', who=0):
        """ put the feedback information on session """
        self.__setSession('user_name', name)
        self.__setSession('user_email', email)
        self.__setSession('user_comments', comments)
        self.__setSession('user_who', who)

    def delFeedbackSession(self):
        """delete feedback information from session """
        self.__delSession('user_name')
        self.__delSession('user_email')
        self.__delSession('user_comments')
        self.__delSession('user_who')

    def getSessionFeedbackName(self, default=''):
        return self.__getSession('user_name', default)

    def getSessionFeedbackEmail(self, default=''):
        return self.__getSession('user_email', default)

    def getSessionFeedbackComments(self, default=''):
        return self.__getSession('user_comments', default)

    def getSessionFeedbackWho(self, default=''):
        return self.__getSession('user_who', default)
