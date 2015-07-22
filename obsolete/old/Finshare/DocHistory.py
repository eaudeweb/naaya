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
# Author(s):
# Alexandru Ghica - Finsiel Romania


#Python imports

#Zope imports
from Globals import InitializeClass

#Product imports
from Products.Finshare.utils import utils
from Products.Finshare.Constants import *


class DocHistory(utils):
    """ Defines a DMHistory """

    def __init__(self):
        """ Constructor """
        self.__histories = {}

    def __create_history(self, p_history_uid, p_history_action):
        """ creates a history entry, a tuple of : current data, current authenticated user and user action """
        self.__histories[p_history_uid] = (self.utGetTodayDate(), self.REQUEST.AUTHENTICATED_USER.getUserName(), p_history_action)
        self._p_changed = 1

    def __get_history(self, p_history_uid):
        """ returns the data for a history entry """
        try: return self.__histories[p_history_uid]
        except: return None
        
    def __delete_history(self, p_history_uid):
        """ deletes a history entry """
        raise EXCEPTION_NOTIMPLEMENTED

    def getHistories(self):
        """ returns the dictionary of histories """
        l_list = []
        for k in self.__histories.keys():
            l_list.append({'id':k, 'date':self.__histories[k][0]})
        self.utSortListOfDictionariesByKey(l_list, 'date', 1)
        return l_list

    def getHistory(self, p_history_uid=None):
        """ returns given history entry """
        return self.__get_history(p_history_uid)

    def createHistory(self, p_history_action):
        """ creates a history entry """
        l_history_uid = self.utGenerateUID()
        self.__create_history(l_history_uid, p_history_action)

InitializeClass(DocHistory)