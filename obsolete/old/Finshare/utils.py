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
# Author(s):
# Alexandru Ghica, Adriana Baciu, Dragos Chirila - Finsiel Romania


#Python imports
import operator
import string
import calendar
from whrandom import choice
import re
from copy import deepcopy
import md5
import base64

#Zope imports
from Products.PythonScripts.standard import url_quote, html_quote
from DateTime import DateTime

#constants
bad_chars = ' ,+&;()[]{}\xC4\xC5\xC1\xC0\xC2\xC3' \
    '\xE4\xE5\xE1\xE0\xE2\xE3\xC7\xE7\xC9\xC8\xCA\xCB' \
    '\xC6\xE9\xE8\xEA\xEB\xE6\xCD\xCC\xCE\xCF\xED\xEC' \
    '\xEE\xEF\xD1\xF1\xD6\xD3\xD2\xD4\xD5\xD8\xF6\xF3' \
    '\xF2\xF4\xF5\xF8\x8A\x9A\xDF\xDC\xDA\xD9\xDB\xFC' \
    '\xFA\xF9\xFB\xDD\x9F\xFD\xFF\x8E\x9E'

good_chars= '___________AAAAAA' \
    'aaaaaaCcEEEE' \
    'EeeeeeIIIIii' \
    'iiNnOOOOOOoo' \
    'ooooSssUUUUu' \
    'uuuYYyyZz'

TRANSMAP = string.maketrans(bad_chars, good_chars)


class utils:
    """ utils class """

    def __init__(self):
        """ constructor """
        pass

    #################
    #   FILE STUFF  #
    #################

    def utGetRoot(self):
        """ get the root object"""
        return self.unrestrictedTraverse(('',))

    def utRead(self, p_path, p_flag='r'):
        """ reads a file """
        return open(p_path, p_flag).read()


    #################
    #   LISTS STUFF #
    #################

    def utConvertToList(self, something):
        """ convert to list """
        ret = something
        if type(something) is type(''):
            ret = [something]
        return ret

    def addToList(self, l, v):
        """ return a new list, after adding value v """
        res = deepcopy(l)
        try:
            res.append(v)
        except:
            pass
        return res

    def removeFromList(self, l, v):
        """ return a new list, after removing value v """
        res = deepcopy(l)
        try:
            res.remove(v)
        except:
            pass
        return res

    def isEmptyList(self, p_list):
        """ test if it's an empty list """
        if (len(p_list) == 0) or (len(p_list) == 1 and p_list[0]==''):
            return 1
        return 0

    def isInList(self, l, v):
        """ return true if value v is in list l """
        return (v in l)

    def isInLines(self, l, v):
        """ test if a string is in a lines variable"""
        l = self.utConvertToList(l)
        return (v in l)

    def utJoinToString(self, something, separator='/'):
        """ get a list [value1, values...], and returns a string like value1<separator>value2... """
        return separator.join(self.utConvertToList(something))

    def utJoinToList(self, l):
        """ gets a list and returns a comma separated string """
        return string.join(l, ',')

    def utSplitToList(self, something, separator='/'):
        """ get a string like value1<separator>value2..., and returns a list [value1, values...] """
        if something == '':
            return []
        else:
            return string.split(something, separator)

    def utElimintateDuplicates(self, p_objects):
        """ eliminate duplicates from a list of objects (with ids) """
        dict = {}
        for l_object in p_objects:
            dict[l_object.id] = l_object
        return dict.values()

    def utSortObjsListByAttr(self, p_list, p_attr, p_desc=0):
        """ sorts a list of objects by an attribute values """
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc:
            l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)

    def utFilterObjsListByAttr(self, p_list, p_attr, p_value):
        """ filter a list of objects by an attribute value """
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), (p_value,)*l_len, p_list)        
        l_temp = filter(lambda x: x[0]==x[1], l_temp)        
        return map(operator.getitem, l_temp, (-1,)*len(l_temp))

    def utSortListOfDictionariesByKey(self, p_list, p_key, p_order=0):
        """ sorts a list of dictionary by key """
        if p_order==0:   #ascending
            p_list.sort(lambda x, y, param=p_key: cmp(x[param], y[param]))
        else:           #desceding
            p_list.sort(lambda x, y, param=p_key: cmp(y[param], x[param]))

    def utConvertLinesToList(self, value):
        """ takes a value from a textarea control and returns a list of values """
        if type(value) == type([]):
            return value
        if value == '':
            return []
        else:
            values = []
            for v in string.split(value , '\r\n'):
                if v != '':
                    values.append(v)
        return values

    #####################
    #   RANDOM IDS/KEYS #
    #####################

    def utGenRandomId(self, p_length=10, p_chars=string.digits):
        """ generate a random numeric id """
        return ''.join([choice(p_chars) for i in range(p_length)])

    def utGenRandomKey(self, p_length=10, p_chars=string.letters + string.digits):
        """ generate a random alpha-numeric key """
        return ''.join([choice(p_chars) for i in range(p_length)])

    def utGenerateUID(self, p_string=''):
        """ generate an UID based on current time and a random string """
        if p_string == '': p_string = '%s%s' % (DateTime(), self.utGenRandomId())
        return md5.new(p_string).hexdigest()

    def utCleanupId(self, p_id=''):
        """ cleanup """
        return p_id.translate(TRANSMAP)


    #####################
    #   STRING STUFF    #
    #####################

    def utStrIsNotEmpty(self, p_str):
        """ test if a string is empty or contains only spaces """
        if len(p_str)==0 or len(re.sub("[' ', '\r\n']", '', p_str))==0: return 0
        return 1

    def utStrAllNotEmpty(self, p_str1, p_str2, p_str3):
        """ test if all strings are not empty """
        if self.utStrIsNotEmpty(p_str1): return 1
        elif self.utStrIsNotEmpty(p_str2): return 1
        elif self.utStrIsNotEmpty(p_str3): return 1
        return 0

    def utStrEscapeForSearch(self, p_string):
        """ escape some characters """
        return re.sub('[(\"{})\[\]]', '', p_string)


    #################
    #   ENCODING    #
    #################

    def utNoneToEmpty(self, value):
        """ """
        if value == None: return ''
        else: return value

    def utEmptyToNone(self, value):
        """ """
        if value == '': return None
        else: return value

    def utHtmlEncode(self, p_string):
        """ encode a string using html_quote """
        return html_quote(p_string)

    def utUrlEncode(self, p_string):
        """ encode a string using url_encode """
        return url_quote(p_string)

    def utJsEncode(self, p_string):
        """ encode a string for javascript processing """
        l_tmp = p_string
        l_tmp = string.replace(l_tmp, '\\', '\\\\')
        l_tmp = string.replace(l_tmp, '\'', '\\\'')
        l_tmp = string.replace(l_tmp, '\"', '\\\"')
        return l_tmp

    def utTextareaEncode(self, p_string):
        """ encode a string (from a textarea control):
          - HTMLEncode str
          - replace \n with <br> """
        l_tmp = self.utHtmlEncode(p_string)
        l_tmp = l_tmp.replace('\n', '<br>')
        return l_tmp

    def utXmlEncode(self, p_string):
        """ encode some special chars """
        l_tmp = str(p_string)
        l_tmp = l_tmp.replace('&', '&amp;')
        l_tmp = l_tmp.replace('<', '&lt;')
        l_tmp = l_tmp.replace('"', '&quot;')
        l_tmp = l_tmp.replace('\'', '&apos;')
        l_tmp = l_tmp.replace('>', '&gt;')
        return l_tmp

    def utBase64Encode(self, p_string):
        """ """
        return base64.encodestring(p_string)

    def utBase64Decode(self, p_string):
        """ """
        try: return base64.decodestring(p_string)
        except: return ''


    ###############################
    # SPECIFIC DATE/TIME METHODS  #
    ###############################

    def utGetTodayDate(self):
        """ returns today date in a DateTime object """
        return DateTime()

    def utGetDate(self, p_string):
        """ returns a string in DateTime format """
        try: return DateTime(p_string)
        except: return None

    def utShowDateTime(self, p_date):
        """ date is a DateTime object. This function returns a string 'dd month_name yyyy' """
        try:
            return p_date.strftime('%d %b %Y')
        except:
            return ''

    def utShowFullDateTime(self, p_date):
        """ date is a DateTime object. This function returns a string 'dd month_name yyyy hh:mm:ss' """
        try:
            return p_date.strftime('%d %b %Y %H:%M')
        except:
            return ''

    def utConvertStringToDateTimeObj(self, p_datestring, p_separator='/'):
        """ takes a string that represents a date like 'dd/mm/yyyy' and returns a DateTime object """
        if p_datestring != '':
            l_dateparts = p_datestring.split(p_separator)
            l_intYear = int(l_dateparts[2], 10)
            l_intMonth = int(l_dateparts[1], 10)
            l_intDay = int(l_dateparts[0], 10)
            return DateTime(str(l_intYear) + '/' + str(l_intMonth) + '/' + str(l_intDay) + ' 00:00:00')
        else:
            return None


    ##################
    #    Emails      #
    ##################

    def utIsEmailValid(self, email, bad_domains=''):
        """ check is email valid """
        if type(bad_domains) == type([]) and len(bad_domains) > 0:
            for dom in bad_domains:
                if re.compile('@'+dom).search(email) is not None:
                    return 0
        if re.compile('\s').search(email) is not None:
            return 0
        if re.compile(r'^[_\-\'\.0-9a-z]+@([0-9a-z][_\-0-9a-z\.]+)\.([a-z]{2,4}$)', re.IGNORECASE).search(email) is None:
            return 0
        return 1


class batch_utils:
    """ """
    def __init__(self, p_num_result, p_nbr_row, p_cur_position):
        """ """
        self.num_result = int(p_num_result)
        self.nbr_row = int(p_nbr_row)
        self.cur_position = int(p_cur_position)

    def __getNumberOfPages(self):
        """ """
        l_number_pages, l_remainder = divmod(self.nbr_row, self.num_result)
        if l_remainder != 0:
            l_number_pages = l_number_pages + 1
        return l_number_pages

    def __getCurrentPage(self):
        """ """
        l_current_page, l_remainder = divmod(self.cur_position * self.__getNumberOfPages(), self.nbr_row)
        return l_current_page

    def __getPagesArray(self):
        """ """
        l_pages = []
        l_current_page = self.__getCurrentPage()
        l_pages_number = self.__getNumberOfPages()
        for i in range(max(0, l_current_page - self.num_result + 1), l_current_page):
            l_pages.append(i)
        for i in range(l_current_page, min(l_current_page + self.num_result, l_pages_number)):
            l_pages.append(i)
        return l_pages

    def butGetPagingInformations(self):
        """ """
        l_start = self.cur_position
        if self.cur_position + self.num_result >= self.nbr_row:
            l_stop = self.nbr_row
            l_next = -1
        else:
            l_stop = self.cur_position + self.num_result
            l_next = self.cur_position + self.num_result
        l_total = self.nbr_row
        if self.cur_position != 0:
            l_prev = self.cur_position - self.num_result
        else:
            l_prev = -1
        l_pages = self.__getPagesArray()
        l_current_page = self.__getCurrentPage()
        l_records_page = self.num_result
        return (l_start, l_stop, l_total, l_prev, l_next, l_current_page, l_records_page, l_pages)


#constants
_SESSION_ERRORS = "site_errors"
_SESSION_INFO = "site_infos"

class session:
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
    def setUserSession(self, name, role, firstname, lastname, email, password='', 
                organisation='', comments='', location=''):
        """ put the user information on session """
        self.__setSession('user_name', name)
        self.__setSession('user_role', role)
        #self.__setSession('user_domains', domains)  #not used for the moment
        self.__setSession('user_firstname', firstname)
        self.__setSession('user_lastname', lastname)
        self.__setSession('user_email', email)
        self.__setSession('user_password', password)
        self.__setSession('user_organisation', organisation)
        self.__setSession('user_comments', comments)
        self.__setSession('user_location', location)

    def delUserSession(self):
        """ delete user information from session """
        self.__delSession('user_name')
        self.__delSession('user_role')
        #self.__delSession('user_domains')
        self.__delSession('user_firstname')
        self.__delSession('user_lastname')
        self.__delSession('user_email')
        self.__delSession('user_password')
        self.__delSession('user_organisation')
        self.__delSession('user_comments')
        self.__delSession('user_location')

    def getSessionUserName(self, default=''):
        return self.__getSession('user_name', default)

    def getSessionUserRoles(self, default=''):
        return self.__getSession('user_role', default)

#    def getSessionUserDomains(self, default=''):
#        return self.__getSession('user_domains', default)

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