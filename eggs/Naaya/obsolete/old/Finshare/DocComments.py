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


class DocComments(utils):
    """ Defines a DMComments """

    def __init__(self):
        """ Constructor """
        self.__comments = {}

    def __create_comment(self, p_comment_uid, p_comment_title, p_comment_text, p_comment_email):
        """ creates a comment entry, a tuple of : current data, current authenticated user and comment's text """
        self.__comments[p_comment_uid] = (self.utGetTodayDate(), self.REQUEST.AUTHENTICATED_USER.getUserName(), p_comment_title, p_comment_text, p_comment_email)
        self._p_changed = 1

    def __get_comment(self, p_comment_uid):
        """ returns the data for a comment entry """
        try: return self.__comments[p_comment_uid]
        except: return None
        
    def delete_comment(self, p_comment_uid):
        """ deletes a comment entry """
        del self.__comments[p_comment_uid]
        self._p_changed = 1

    def getComments(self):
        """ returns the dictionary of comments """
        l_list = []
        for k in self.__comments.keys():
            l_list.append({'id':k, 'date':self.__comments[k][0]})
        self.utSortListOfDictionariesByKey(l_list, 'date', 1)
        return l_list

    def getComment(self, p_comment_uid=None):
        """ returns given comment entry """
        return self.__get_comment(p_comment_uid)    
        
    def createComment(self, p_comment_title, p_comment_text, p_comment_email):
        """ creates a comment entry """
        l_comment_uid = self.utGenerateUID()
        self.__create_comment(l_comment_uid, p_comment_title, p_comment_text, p_comment_email)

InitializeClass(DocComments)