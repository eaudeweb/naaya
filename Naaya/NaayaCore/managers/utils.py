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
import operator
import string
import calendar
from whrandom import choice
import re
from copy import deepcopy
import md5
import base64
import urllib
import time

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

class list_utils:
    """Provides some interface to handle a list of ids: add/remove id from list"""

    def __init__(self):
        """Constructor"""
        pass

    def splitToList(self, s):
        """Gets a comma separated string and returns a list"""
        res = []
        if s!='':
            res = s.split(',')
        return res

    def joinToList(self, l):
        """Gets a list and returns a comma separated string"""
        return string.join(l, ',')

    def addToList(self, l, v):
        """Return a new list, after adding value v"""
        res = deepcopy(l)
        try: res.append(v)
        except: pass
        return res

    def removeFromList(self, l, v):
        """Return a new list, after removing value v"""
        res = deepcopy(l)
        try: res.remove(v)
        except: pass
        return res

    def isInList(self, l, v):
        """Return true if value v is in list l"""
        return (v in l)

    def isInLines(self, l, v):
        """ test if a string is in a lines variable"""
        l = self.convertToList(l)
        return (v in l)

    def convertToList(self, l):
        """ convert to list """
        if type(l) != type([]):
            l = [l]
        return l

class file_utils:
    """ """

    def __init__(self):
        """ """
        pass

    def futRead(self, p_path, p_flag='r'):
        """ """
        return open(p_path, p_flag).read()

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

class utils:
    """Utils class"""

    def __init__(self):
        """Constructor"""
        pass

    def utGetROOT(self):
        """ get the ROOT object"""
        return self.unrestrictedTraverse(('',))

    def utGetItems(self, p_metatype=None, p_except=[]):
        """ get all items coresponding with p_metatype"""
        l_results = []
        for object in self.objectValues(p_metatype):
            if object.meta_type not in p_except:
                l_results.append(object)
        return l_results

    def utGetObject(self, path=None):
        """ get an object by path """
        try: return self.unrestrictedTraverse(path)
        except: return None

    #####################
    #   RANDOM IDS/KEYS #
    #####################
    def utGenRandomId(self, p_length=10, p_chars=string.digits):
        """Generate a random numeric id."""
        return ''.join([choice(p_chars) for i in range(p_length)])

    def utGenRandomKey(self, p_length=10, p_chars=string.letters + string.digits):
        """Generate a random alpha-numeric key."""
        return ''.join([choice(p_chars) for i in range(p_length)])

    def utGenerateUID(self, p_string=''):
        """ Generate an UID based on current time and a random string """
        if p_string == '': p_string = '%s%s' % (time.time(), self.utGenRandomId())
        return md5.new(p_string).hexdigest()

    def utCleanupId(self, p_id=''):
        """ """
        return p_id.translate(TRANSMAP)

    #################
    #   LISTS STUFF #
    #################
    def utConvertToList(self, something):
        """Convert to list"""
        ret = something
        if type(something) is type(''):
            ret = [something]
        return ret

    def utSplitToList(self, something, separator='/'):
        """Get a string like value1<separator>value2..., and returns a list [value1, values...]"""
        if something == '':
            return []
        else:
            return str(something).split(separator)

    def utConvertLinesToList(self, value):
        """Takes a value from a textarea control and returns a list of values"""
        if type(value) == type([]):
            return value
        elif value == '':
            return []
        else:
            return filter(lambda x:x!='', value.split('\r\n'))

    def utConvertListToLines(self, values):
        """Takes a list of values and returns a value for a textarea control"""
        if len(values) == 0: return ''
        else: return '\r\n'.join(values)

    def utListDifference(self, p_l1, p_l2):
        #return a list with elements from p_l1 that are not in p_l2
        return [l_e1 for l_e1 in p_l1 if l_e1 not in p_l2]

    def utListIntersection(self, p_l1, p_l2):
        #return the intersection of two lists
        return [l_e1 for l_e1 in p_l1 if l_e1 in p_l2]

    def utJoinToString(self, something, separator='/'):
        """Get a list [value1, values...], and returns a string like value1<separator>value2..."""
        return separator.join(self.utConvertToList(something))

    def utSortObjsListByAttr(self, p_list, p_attr, p_desc=1):
        """Sort a list of objects by an attribute values"""
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc:
            l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)

    def utSortDictsListByKey(self, p_list, p_key, p_desc=1):
        """Sort a list of objects by an item values"""
        l_len = len(p_list)
        l_temp = map(None, map(lambda x, y: x[y], p_list, (p_key,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc:
            l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)

    def utFilterObjsListByAttr(self, p_list, p_attr, p_value):
        """Filter a list of objects by an attribute value"""
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), (p_value,)*l_len, p_list)
        l_temp = filter(lambda x: x[0]==x[1], l_temp)
        return map(operator.getitem, l_temp, (-1,)*len(l_temp))

    def utSortListOfDictionariesByKey(self, p_list, p_key, p_order=0):
        """ Sort a list of dictionary by key """
        if p_order==0:   #ascending
            p_list.sort(lambda x, y, param=p_key: cmp(x[param], y[param]))
        else:           #desceding
            p_list.sort(lambda x, y, param=p_key: cmp(y[param], x[param]))

    #################
    #   FORMS STUFF #
    #################
    def utAddObjectAction(self, REQUEST=None):
        """Check if adding an object"""
        try: return REQUEST.has_key('add')
        except: return 0

    def utUpdateObjectAction(self, REQUEST=None):
        """Check if updating an object"""
        try: return REQUEST.has_key('update')
        except: return 0

    def utDeleteObjectAction(self, REQUEST=None):
        """Check if deleting an object"""
        try: return REQUEST.has_key('delete')
        except: return 0

    def utImportObjectAction(self, REQUEST=None):
        """Check if import action"""
        try: return REQUEST.has_key('import')
        except: return 0

    def utRefreshObjectAction(self, REQUEST=None):
        """Check if refresh action"""
        try: return REQUEST.has_key('refresh')
        except: return 0

    def utSetFormError(self, req, key, msg):
        req.set('FORM_ERROR', 1)
        req.set('FORM_ERROR_' + key, msg)
        return req

    def utGetRefererIp(self, REQUEST=None):
        l_request_ip = 'unknown'
        if REQUEST is not None:
            l_request_ip = REQUEST.get('HTTP_X_FORWARDED_FOR', '')
            if l_request_ip == '':
                l_request_ip = REQUEST.get('REMOTE_ADDR', 'unknown')
        return l_request_ip

    #####################
    #   STRING STUFF    #
    #####################
    def utStrStrip(self, p_value):
        """removes leadeaing and trailing white spaces"""
        return string.strip(p_value)

    def utStrSplit(self, p_value, p_separator):
        """splits a string"""
        return string.split(p_value, p_separator)

    def utStrJoin(self, p_list, p_separator):
        """joins a list of strings"""
        return p_separator.join(p_list)

    def utStrReplace(self, p_string, p_old, p_new):
        """replace"""
        return string.replace(p_string, p_old, p_new)

    def utStrEscapeForSearch(self, p_string):
        """ escape some characters"""
        return re.sub('[(\"{})\[\]]', '', p_string)

    def utStrEscapeHTMLTags(self, p_string):
        """ escape HTML tags from string """
        strip_html_pattern = re.compile(r'<[^>]*>')
        plaintext = strip_html_pattern.sub('',p_string)
        return plaintext

    def utTruncateString(self, p_string, p_len=14):
        #given a string if the length of the string is bigger
        #than the given length then truncate the string
        if len(p_string) > p_len: return '%s..' % p_string[0:p_len]
        else: return p_string
    
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
        """Encode a string using html_quote"""
        return html_quote(p_string)

    def utUrlEncode(self, p_string):
        """Encode a string using url_encode"""
        return url_quote(p_string)

    def utJsEncode(self, p_string):
        """Encode a string for javascript processing"""
        l_tmp = str(p_string)
        l_tmp = l_tmp.replace('\\', '\\\\')
        l_tmp = l_tmp.replace('\'', '\\\'')
        l_tmp = l_tmp.replace('\"', '\\\"')
        return l_tmp

    def utTextareaEncode(self, p_string):
        """Encode a string (from a textarea control):
          - HTMLEncode str
          - replace \n with <br>"""
        l_tmp = self.utHtmlEncode(p_string)
        l_tmp = l_tmp.replace('\n', '<br>')
        return l_tmp

    def utXmlEncode(self, p_string):
        """Encode some special chars"""
        if isinstance(p_string, unicode): l_tmp = p_string.encode('utf-8')
        else: l_tmp = str(p_string)
        l_tmp = l_tmp.replace('&', '&amp;')
        l_tmp = l_tmp.replace('<', '&lt;')
        l_tmp = l_tmp.replace('"', '&quot;')
        l_tmp = l_tmp.replace('\'', '&apos;')
        l_tmp = l_tmp.replace('>', '&gt;')
        return l_tmp

    def utToUtf8(self, p_string):
        #converts the value to utf8
        if isinstance(p_string, unicode): p_string = p_string.encode('utf-8')
        return p_string

    def utBase64Encode(self, p_string):
        """ """
        return base64.encodestring(p_string)

    def utBase64Decode(self, p_string):
        """ """
        try: return base64.decodestring(p_string)
        except: return ''

    def utShowSizeKb(self, p_size):
        """ transform a file size in Kb """
        return int(p_size/1024 + 1)

    def utUnquote(self, value):
        #transform escapes in single characters
        return urllib.unquote(value)

    #####################
    # BROWSER DETECTION #
    #####################
    #
    # taken from http://www.zopelabs.com/cookbook/990728167
    # Submitted by: andyman232323
    #
    # 10x a lot!
    #
    def utGetBrowserType(self, p_http_user_agent):
        """Get browser type"""
        l_browsertype = ''
        if ((string.find(p_http_user_agent, 'MSIE') == -1) and (string.find(p_http_user_agent, 'Mozilla') >= 0)):
            if (string.find(p_http_user_agent, 'Gecko') > -1):
                l_browsertype = 'nn6'
            else:
                l_browsertype = 'nn4'
        elif (string.find(p_http_user_agent, 'MSIE') >= 0):
            l_browsertype = 'ms'
        else:
            l_browsertype = 'unknown'
        return l_browsertype

    def utIsBrowserIE(self):
        """Is Internet Explorer"""
        return (self.utGetBrowserType(self.REQUEST['HTTP_USER_AGENT']) == 'ms')

    def utIsBrowserNN(self):
        """Is Netscape Navigator"""
        l_browsertype = self.utGetBrowserType(self.REQUEST['HTTP_USER_AGENT'])
        return ((l_browsertype == 'nn4') or (l_browsertype == 'nn6'))


    ###############################
    # SPECIFIC DATE/TIME METHODS  #
    ###############################
    def utGetTodayDate(self):
        """Returns today date in a DateTime object"""
        return DateTime()

    def utGetDate(self, p_string):
        """ """
        try: return DateTime(p_string)
        except: return None

    def utConvertMDYToDateTime(self, p_month, p_day, p_year):
        """takes 3 values and returns a DateTime object"""
        return (DateTime(str(p_month) + '/' + str(p_day) + '/' + str(p_year)))

    def utShowDateTime(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy'"""
        try: return p_date.strftime('%d %b %Y')
        except: return ''

    def utShowFullDateTime(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy hh:mm:ss'"""
        try: return p_date.strftime('%d %b %Y %H:%M:%S')
        except: return ''

    def utShowFullDateTimeHTML(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy hh:mm:ss'"""
        try: return p_date.strftime('%Y-%m-%dT%H:%M:%S')
        except: return ''

    def utGetIdFromStringDate(self, p_datestring, p_separator='/'):
        """Takes a string that reprezents a date like 'dd/mm/yyyy' and returns a string 'ddmmyyyy'"""
        return string.replace(p_datestring, p_separator, '')

    def utConvertValuesToDateTimeObj(self, p_year, p_month, p_day):
        """Takes 3 values for year, month, day and returns a DateTime object"""
        return DateTime(str(p_year) + '/' + str(p_month) + '/' + str(p_day) + ' 00:00:00')

    def utConvertStringToDateTimeObj(self, p_datestring, p_separator='/'):
        """Takes a string that represents a date like 'dd/mm/yyyy' and returns a DateTime object"""
        try:
            l_dateparts = p_datestring.split(p_separator)
            l_intYear = int(l_dateparts[2], 10)
            l_intMonth = int(l_dateparts[1], 10)
            l_intDay = int(l_dateparts[0], 10)
            return DateTime(str(l_intYear) + '/' + str(l_intMonth) + '/' + str(l_intDay) + ' 00:00:00')
        except:
            return None

    def utConvertDateTimeObjToString(self, p_date, p_separator='/'):
        """Takes a string that represents a date like 'dd/mm/yyyy' and returns a DateTime object"""
        if p_date:
            l_year = str(p_date.year())
            l_month = str(p_date.month())
            l_day = str(p_date.day())
            if len(l_month)==1:
                l_month = '0' + l_month
            if len(l_day)==1:
                l_day = '0' + l_day
            return l_day + p_separator + l_month + p_separator + l_year
        else:
            return ''

    def utGetJulianDayNumber(self, p_date):
        """Returns the Julian day number of a date."""
        l_year = p_date.year()
        l_month = p_date.month()
        l_day = p_date.day()
        a = (14 - l_month)/12
        y = l_year + 4800 - a
        m = l_month + 12*a - 3
        return l_day + ((153*m + 2)/5) + 365*y + y/4 - y/100 + y/400 - 32045

    def utCheckDate(self, p_datestring, p_separator='/'):
        """This functions takes a string that reprezents a date like 'dd/mm/yyyy' and tests is a valide date."""
        l_isDate = 1
        l_daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        l_dateparts = string.split(p_datestring, p_separator)
        if len(l_dateparts) != 3:
            l_isDate = 0
        else:
            l_intYear = l_dateparts[2]
            l_intMonth = l_dateparts[1]
            l_intDay = l_dateparts[0]
            try:
                l_intYear = int(l_intYear, 10)
                l_intMonth = int(l_intMonth, 10)
                l_intDay = int(l_intDay, 10)
            except:
                l_isDate = 0
            else:
                if (l_intYear <= 50):
                    l_intYear += 2000
                if (l_intYear >= 51 and l_intYear < 100):
                    l_intYear += 1900
                if ((l_intMonth==0) or (l_intMonth > 12) or (l_intDay == 0) or (l_intYear > 9999)):
                    l_isDate = 0
                else:
                    if (l_intMonth == 2): #february
                        if calendar.isleap(l_intYear):
                            l_nDays = 29
                        else:
                            l_nDays = 28
                    else:
                        l_nDays = l_daysInMonth[l_intMonth-1]
                    if (l_intDay > l_nDays):
                        l_isDate = 0
        return l_isDate

    def utformatDate(self, date, format='%Y-%m-%d %H:%M'):
        """ format a date according with specified format """
        try:
            return date().strftime(format)
        except AttributeError:
            return DateTime(date).strftime(format)
        except:
            return None

    def utCheckDates(self, p_startDate, p_endDate):
        """This function takes 2 date string and test that startDate <= endDate"""
        return (self.utConvertStringToDateTimeObj(p_startDate) <= self.utConvertStringToDateTimeObj(p_endDate))

    def utCheckPeriod(self, p_dateStart1, p_dateEnd1, p_dateStart2, p_dateEnd2, p_separator='/'):
        """This function takes 2 DateTime objects(time interval T1) and 2 other DateTime objects(time interval T2) and validates that T1 includes T2"""
        if not p_dateStart1 and not p_dateEnd1:
            #T1 is undefined
            return 1
        elif p_dateStart1 and not p_dateEnd1:
            #T1 has just start - check that (p_dateStart2 and p_dateEnd2 >= p_dateStart1)
            if p_dateStart2:
                if p_dateStart2 < p_dateStart1:
                    return 0
            if p_dateEnd2:
                if p_dateEnd2 < p_dateStart1:
                    return 0
            return 1
        elif not p_dateStart1 and p_dateEnd1:
            #T1 has just end - check that (p_dateStart2 and p_dateEnd2 <= p_dateEnd1)
            if p_dateStart2:
                if p_dateStart2 > p_dateEnd1:
                    return 0
            if p_dateEnd2:
                if p_dateEnd2 > p_dateEnd1:
                    return 0
            return 1
        else:
            #T1 has start and end - check that (p_dateStart2 and p_dateEnd2 >= p_dateStart1) and (p_dateStart2 and p_dateEnd2 <= p_dateEnd1)
            if p_dateStart2:
                if p_dateStart2 < p_dateStart1 or p_dateStart2 > p_dateEnd1:
                    return 0
            if p_dateEnd2:
                if p_dateEnd2 < p_dateStart1 or p_dateEnd2 > p_dateEnd1:
                    return 0
            return 1

    def utCheckIntervals(self, p_startdate1, p_enddate1, p_startdate2, p_enddate2):
        """Takes 2 intervals and checks if there is an intersection"""
        return not (p_startdate2 > p_enddate1 or p_enddate2 < p_startdate1)

    #####################
    # HTMLizing text    #
    #####################
    #http://www.faqts.com/knowledge_base/view.phtml/aid/4525
    #Nathan Wallace, Fiona Czuczman
    #Hans Nowak, Snippet 337, Bjorn Pettersen

    def _utTranslate(self, text, pre=0):
        translate_prog = prog = re.compile(r'\b(http|ftp|https)://\S+(\b|/)|\b[-.\w]+@[-.\w]+')
        i = 0
        list = []
        while 1:
            m = prog.search(text, i)
            if not m:
                break
            j = m.start()
            list.append(self._utEscape(text[i:j]))
            i = j
            url = m.group(0)
            while url[-1] in '();:,.?\'"<>':
                url = url[:-1]
            i = i + len(url)
            url = self._utEscape(url)
            if not pre:
                if ':' in url:
                    repl = '<A HREF="%s">%s</A>' % (url, url)
                else:
                    repl = '<A HREF="mailto:%s">&lt;%s&gt;</A>' % (url, url)
            else:
                repl = url
            list.append(repl)
        j = len(text)
        list.append(self._utEscape(text[i:j]))
        return ''.join(list)

    def _utEscape(self, s):
        s = string.replace(s, '&', '&amp;')
        s = string.replace(s, '<', '&lt;')
        s = string.replace(s, '>', '&gt;')
        return s

    def _utEscapeQ(self, s):
        s = self._utEscape(s)
        s = string.replace(s, '"', '&quot;')
        return s
        
    def _utEmphasize(self, line):
        return re.sub(r'\*([a-zA-Z]+)\*', r'<I>\1</I>', line)
        
    def text2html(self, body):
        res = []
        pre = 0
        raw = 0
        for line in string.split(body, '\n'):
            tag = string.lower(string.rstrip(line))
            if tag == '<html>':
                raw = 1
                continue
            if tag == '</html>':
                raw = 0
                continue
            if raw:
                res.append(line)
                continue
            if not string.strip(line):
                if pre:
                    res.append('</PRE>')
                    pre = 0
                else:
                    res.append('<P>')
            else:
                if line[0] not in string.whitespace:
                    if pre:
                        res.append('</PRE>')
                        pre = 0
                else:
                    if not pre:
                        res.append('<PRE>')
                        pre = 1
                if '/' in line or '@' in line:
                    line = self._utTranslate(line, pre)
                elif '<' in line or '&' in line:
                    line = self._utEscape(line)
                if not pre and '*' in line:
                    line = self._utEmphasize(line)
                res.append(line)
        if pre:
            res.append('</PRE>')
            pre = 0
        return string.join(res)
