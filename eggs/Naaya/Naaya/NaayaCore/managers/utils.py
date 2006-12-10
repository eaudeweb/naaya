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
import codecs
from zipfile import *

import csv
import tempfile
import os
from email.Utils import encode_rfc2231

#Zope imports
from Products.PythonScripts.standard import url_quote, html_quote
from DateTime import DateTime
from OFS.ObjectManager import checkValidId

#Product imports
from stripping_tool import stripping_tool

#constants
bad_chars = ' ,+&;\'()[]{}\xC4\xC5\xC1\xC0\xC2\xC3' \
    '\xE4\xE5\xE1\xE0\xE2\xE3\xC7\xE7\xC9\xC8\xCA\xCB' \
    '\xC6\xE9\xE8\xEA\xEB\xE6\xCD\xCC\xCE\xCF\xED\xEC' \
    '\xEE\xEF\xD1\xF1\xD6\xD3\xD2\xD4\xD5\xD8\xF6\xF3' \
    '\xF2\xF4\xF5\xF8\x8A\x9A\xDF\xDC\xDA\xD9\xDB\xFC' \
    '\xFA\xF9\xFB\xDD\x9F\xFD\xFF\x8E\x9E'

good_chars= '____________AAAAAA' \
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

    def stripHTMLTags(self, s):
        """ Takes a text and removes the HTML tags leaving just plain text """
        strip_html_pattern = re.compile(r'<[^>]*>')
        plaintext = strip_html_pattern.sub('', s)
        return plaintext.replace('  ', ' ')

    def splitToList(self, s, separator=','):
        """Gets a comma separated string and returns a list"""
        res = []
        if s!='':
            res = s.split(separator)
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

    def utRemoveDuplicates(self, seq):
        #given a list of something it removes duplicates
        #special case of an empty sequence
        if len(seq) == 0:
            return []
        #try using a dict first, because it's the fastest
        u = {}
        try:
            for x in seq:
                u[x] = 1
        except TypeError:
            del u
        else:
            return u.keys()
        #brute force
        u = []
        for x in s:
            if x not in u:
                u.append(x)
        return u

    def utEliminateDuplicatesByURL(self, p_objects):
        """ eliminate duplicates from a list of objects """
        dict = {}
        for l_object in p_objects:
                dict[l_object.absolute_url()] = l_object
        return dict.values()

class file_utils:
    """ """

    def __init__(self):
        """ """
        pass

    def futRead(self, p_path, p_flag='r'):
        """ """
        return open(p_path, p_flag).read()

    def futReadEnc(self, p_path, p_flag='r', p_encode='utf-8'):
        """ """
        return codecs.open(p_path, p_flag, p_encode).read()

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

    def utGetObject(self, path=None, default=None):
        """ get an object by path """
        try: return self.unrestrictedTraverse(path, default)
        except: return None

    def utGenRandomId(self, p_length=10, p_chars=string.digits):
        """Generate a random numeric id."""
        return ''.join([choice(p_chars) for i in range(p_length)])

    def utGenerateUID(self, p_string=''):
        """ Generate an UID based on current time and a random string """
        if p_string == '': p_string = '%s%s' % (time.time(), self.utGenRandomId())
        return md5.new(p_string).hexdigest()

    def utCleanupId(self, p_id=''):
        """ """
        if isinstance(p_id, unicode): x = p_id.encode('utf-8')
        else: x = str(p_id)
        x = x.strip()
        return x.translate(TRANSMAP)

    def utValidateId(self, p_id=''):
        """."""
        try: checkValidId(self, p_id)
        except Exception, error:
            if str(error) != "('Empty or invalid id specified', '')":
                return [str(error)]
        return None

    def utConvertToList(self, s):
        """Convert to list"""
        if not isinstance(s, list):
            s = [s]
        elif isinstance(s, tuple):
            s = list(s)
        return s

    def utConvertListToLines(self, values):
        """Takes a list of values and returns a value for a textarea control"""
        if len(values) == 0: return ''
        else: return '\r\n'.join(values)

    def utConvertLinesToList(self, value):
        """Takes a value from a textarea control and returns a list of values"""
        if type(value) == type([]): return value
        elif value == '': return []
        else:
            values = []
            for v in value.split('\r\n'):
                if v != '': values.append(v)
        return values

    def utSplitSequence(self, seq, size):
        """
        Split up seq in pieces of size.
        """
        return [seq[i:i+size] for i in range(0, len(seq), size)]

    def utNewlinetoBr(self, p_string):
        #convert new lines to <br /> for html display
        if p_string.find('\r') >= 0: p_string = ''.join(p_string.split('\r'))
        if p_string.find('\n') >= 0: p_string = '<br />'.join(p_string.split('\n'))
        return p_string

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

    def utSortObjsListByMethod(self, p_list, p_method, p_desc=1):
        """Sort a list of objects by an attribute values"""
        l_len = len(p_list)
        l_temp = map(None, map(lambda x, y: getattr(x, y)(), p_list, (p_method,)*l_len), xrange(l_len), p_list)
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

    def utSortListOfDictionariesByKey(self, p_list, p_key, p_order):
        """ Sort a list of dictionary by key """
        if p_order:
            p_list.sort(lambda x, y, param=p_key: cmp(y[param], x[param]))
        else:
            p_list.sort(lambda x, y, param=p_key: cmp(x[param], y[param]))

    def utGetRefererIp(self, REQUEST=None):
        l_request_ip = 'unknown'
        if REQUEST is not None:
            l_request_ip = REQUEST.get('HTTP_X_FORWARDED_FOR', '')
            if l_request_ip == '':
                l_request_ip = REQUEST.get('REMOTE_ADDR', 'unknown')
        return l_request_ip

    def utStrEscapeForSearch(self, p_string):
        """ escape some characters"""
        return re.sub('[(\"{})\[\]]', '', p_string)

    def utStripAllHtmlTags(self, s):
        #removes all html tags from an html string
        p = stripping_tool((), ())
        p.feed(s)
        p.close()
        p.cleanup()
        return ''.join([x.strip() for x in p.result]).replace('&nbsp;', ' ')

    def utStripHtmlTags(self, s, all_tags, single_tags):
        #removes the html tags that are not allowe from a string
        p = striping_tool(all_tags, single_tags)
        try:
            p.feed(s)
            p.close()
        except:
            r = []
        else:
            r = p.result
        p.cleanup()
        return ''.join(r)

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

    def utStripString(self, p_string):
        """ strip a given string """
        return string.strip(self.utToUtf8(p_string))

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
        """Encode a string using url_quote"""
        return url_quote(p_string)

    def utToUtf8(self, p_string):
        #convert to utf-8
        if isinstance(p_string, unicode): return p_string.encode('utf-8')
        else: return str(p_string)

    def utToUnicode(self, p_string):
        #convert to unicode
        if not isinstance(p_string, unicode): return unicode(p_string, 'utf-8')
        else: return p_string

    def utLatinToUTF(self, p_string):
        """ accepts only strings """
        if p_string is None:
            return '-'
        uni = unicode(p_string, 'latin-1')
        return uni.encode('utf-8')

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

    def ut_content_disposition(self, filename=None): 
        """Generate a properly escaped Content-Disposition header""" 
        filename = self.utToUtf8(filename)
        return 'attachment; filename*=%s'% encode_rfc2231(filename, 'utf-8')

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

    def utShowSize(self, p_size):
        #Transform a file size in Kb, Mb ..
        l_bytes = float(p_size)
        l_type = ''
        l_res = ''
        if l_bytes >= 1000:
            l_bytes = l_bytes/1024
            l_type = 'Kb'
            if l_bytes >= 1000:
                l_bytes = l_bytes/1024
                l_type = 'Mb'
            l_res = '%s %s' % ('%4.2f' % l_bytes, l_type)
        else:
            l_type = 'Bytes'
            l_res = '%s %s' % ('%4.0f' % l_bytes, l_type)
        return l_res

    def utUnquote(self, value):
        #transform escapes in single characters
        return urllib.unquote(value)

    def utGetTodayDate(self):
        """Returns today date in a DateTime object"""
        return DateTime()

    def utGetDate(self, p_string):
        """ """
        try: return DateTime(p_string)
        except: return None

    def utShowDateTime(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy'"""
        try: return p_date.strftime('%d/%m/%Y')
        except: return ''

    # generic function, must be replaced for CHM and other sites !!!
    def utShowDateTime1(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy'"""
        try: return p_date.strftime('%d %b %Y')
        except: return ''

    def utStringDate(self, p_date):
        """ """
        try: return p_date.strftime('%d%m%Y')
        except: return ''

    def utShowFullDateTime(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy hh:mm:ss'"""
        try: return p_date.strftime('%d %b %Y %H:%M:%S')
        except: return ''

    def utShowFullDateTimeHTML(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy hh:mm:ss'"""
        try: return p_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        except: return ''

    def utShowDateTimePeriod(self, p_start, p_end):
        """
        Given two dates, returns a string to show the interval.
        """
        if p_start is None and p_end is None:
            return ''
        elif p_start is None:
            return self.utShowDateTime(p_end)
        elif p_end is None:
            return self.utShowDateTime(p_start)
        elif p_start == p_end:
            return self.utShowDateTime(p_start)
        else:
            sd, sm, sy = p_start.day(), p_start.month(), p_start.year()
            ed, em, ey = p_end.day(), p_end.month(), p_end.year()
            if sy == ey:    #same year
                if sm == em:    #same month
                    return '%s - %s' % (sd, self.utShowDateTime(p_end))
                else:
                    return '%s - %s %s' % (p_start.strftime('%d %b'), p_end.strftime('%d %b'), sy)
            else:
                return '%s - %s' % (self.utShowDateTime(p_start), self.utShowDateTime(p_end))

    def utConvertStringToDateTimeObj(self, p_datestring, p_separator='/'):
        """Takes a string that represents a date like 'dd/mm/yyyy' and returns a DateTime object"""
        try:
            l_dateparts = p_datestring.split(p_separator)
            l_intYear = int(l_dateparts[2], 10)
            l_intMonth = int(l_dateparts[1], 10)
            l_intDay = int(l_dateparts[0], 10)
            if l_intMonth<1 or l_intMonth>12: return None
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

    def utConvertDateTimeHTMLToString(self, p_datestring):
        """ """
        try:
            y, m, d = p_datestring.split('T')[0].split('-')
            return '%s/%s/%s' % (d, m, y)
        except:
            return ''

    def utLinkValue(self, url):
        """
        Takes the value of an url and test if is not empty.
        """
        return url != '' and url != 'http://' and url != 'https://'

    def utIsEmptyString(self, p_str):
        """Test if empty string"""
        if p_str:
            if p_str.count(" ") != len(p_str): return 0
        return 1

    def utIsValidDateTime(self, p_str):
        """Test if the string is a valid date"""
        if p_str:
            return type(self.utConvertStringToDateTimeObj(p_str)) == type(DateTime())
        else:
            return 1

    def utIsAbsInteger(self, p_data):
        """Test if the p_data parameter is integer"""
        try:
            p_data = int(p_data)
            return p_data >= 0
        except:
            return 0

    def utIsFloat(self, p_data):
        """Test if the p_data parameter is float"""
        if p_data:
            try:
                p_data = float(p_data)
                return p_data >= 0
            except:
                return 0
        return 1

    def utGenerateZip(self, name, objects, RESPONSE):
        """
        Zip all the requested objects. Each object must implement
        the B{getZipData} method, otherwise empty content will be provided.
        @param name: the name of the archive (wihtout .zip extension!!!)
        @type name: string
        @param objects: a list of objects
        @type objects: list
        """
        path = CLIENT_HOME
        if not os.path.isdir(path):
            try: os.mkdir(path)
            except: raise OSError, 'Can\'t create directory %s' % path
        tempfile.tempdir = path
        tmpfile = tempfile.mktemp(".temp")
        zf = ZipFile(tmpfile,"w")
        sz = 0
        for o in objects:
            sz = sz + float(o.get_size())
            timetuple = time.localtime()[:6]
            filename = name + '/' + self.utToUtf8(o.id)
            zfi = ZipInfo(filename)
            zfi.date_time = timetuple
            zfi.compress_type = ZIP_DEFLATED
            try: zf.writestr(zfi, o.getZipData())
            except: zf.writestr(zfi, '')
        zf.close()
        stat = os.stat(tmpfile)
        content = open(tmpfile, 'rb').read()
        os.unlink(tmpfile)
        RESPONSE.setHeader('Content-Type', 'application/x-zip-compressed')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % name)
        RESPONSE.setHeader('Content-Length', stat[6])
        return content

class tmpfile:

    def __init__(self, data):
        self.fname = tempfile.mktemp()
        writer = csv.writer(open(self.fname,'wb'))
        for row in data:
            writer.writerow(row)

    def __str__(self): return self.fname
    __repr__ = __str__

    def __del__(self):
        os.unlink(self.fname)

class ZZipFile(ZipFile):

    def read(self,size=-1):
        """ """
        if(self.hasbeenread == 0):
            self.hasbeenread = 1
            return ZipFile.read(self,self.filename)
        else:
            return ""

    def seek(self):
        """ Ignore since it is only used to figure out size """
        self.hasbeenread = 0
        return 0

    def tell(self):
        """ """
        return self.getinfo(filename).file_size

    def setcurrentfile(self,filename):
        """ """
        self.hasbeenread = 0
        self.filename=filename
