import operator
import string
from random import choice
import re
from copy import deepcopy
import md5
import base64
import urllib
import time
import codecs
from zipfile import *
from BeautifulSoup import BeautifulSoup

import csv
import tempfile
import os
import pickle
from email.Utils import encode_rfc2231
from urllib import urlencode
from StringIO import StringIO
from unidecode import unidecode
from warnings import warn

from Products.PythonScripts.standard import url_quote, html_quote
from DateTime import DateTime
from OFS.ObjectManager import checkValidId

from Products.NaayaCore.managers.paginator import ObjectPaginator
from naaya.core.utils import force_to_unicode, unescape_html_entities
from naaya.core.zope2util import DT2dt

from lxml.builder import ElementMaker

#constants

default_remove_words = [
    "a", "an", "as", "at", "before", "but", "by", "for", "from", "is",
    "in", "into", "like", "of", "off", "on", "onto", "per", "since",
    "than", "the", "this", "that", "to", "up", "via", "with",
]

default_remove_lead = ['_', 'aq_']

default_remove_trail = ['__']

def genObjectId(s, num_chars=80, removelist=None):
    '''
    DEPRECATED! Use slugify(s)

    Changes, e.g., "Petty theft" to "petty-theft".
    This function is the Python equivalent of the javascript function
        of the same name in django/contrib/admin/media/js/urlify.js.
    It can get invoked for any field that has a prepopulate_from
        attribute defined, although it only really makes sense for
        SlugFields.

    NOTE: this implementation corresponds to the Python implementation
          of the same algorithm in django/contrib/admin/media/js/urlify.js
    '''
    warn('genObjectId is deprecated. Use slugify(s) instead',
         DeprecationWarning, stacklevel=2)
    return slugify(s,num_chars,removelist)

def toAscii(s):
    '''
    Functionality now in charge of unidecode
    '''
    return unidecode(s)

def slugify(s, maxlen=80, removelist=None):
    '''
    Converts unicode to ascii string ready for use in urls/zope id-s
    You can use the returned value as a param for uniqueId(id,exists)
    to get an available valid id in context.

      * `s`: unicode string. However, if a `str` is provided,
        it's decoded to `unicode` using the "ascii" encoding.
      * `maxlen`: maximum length of string
      * `removelist`: list of words to be removed from id.

    If None, a common En. wordlist will be used (default_remove_words)

    Uses unidecode, converts group of spaces/unacceptable chars
    to single hyphens. Strips leading/trailing hyphens, lowers case,
    returns random 5-digit word if id can not be constructed from input.

    '''
    if maxlen <= 0:
        raise ValueError("Illegal value for @param maxlen")
    if type(s) is str:
        s = force_to_unicode(s) # raises UnicodeDecodeError if non-ascii
        # coder should take notice `s` must be unicode / ascii str

    s = str(unidecode(s))

    if removelist is None:
        if s.lower() in default_remove_words:
            # if the id as a whole is already in default_remove_words
            # it should be kept
            removelist = []
        else:
            removelist = default_remove_words

    ignore_words = '|'.join([r for r in removelist])
    ignore_words_pat = re.compile(r'\b('+ignore_words+r')\b', re.I)
    ignore_chars_pat = re.compile(r'[^-_\.A-Z0-9\s]', re.I)
    outside_space_pat = re.compile(r'^[-\s]+|[-\s]+$')
    inside_space_pat = re.compile(r'[-\s]+')

    s = ignore_words_pat.sub('', s)  # remove unimportant words
    s = ignore_chars_pat.sub('-', s) # change unneeded chars to hyphens
    s = outside_space_pat.sub('', s) # trim leading/trailing spaces/hyphens
    s = inside_space_pat.sub('-', s) # convert spaces or group of spaces/hyphens to single hyphens

    wordlist = s.split('-')
    picked_words=[]
    for w in wordlist:
        if (sum([len(x) for x in picked_words])+len(picked_words)+len(w)) <= maxlen:
            picked_words.append(w)
        else:
            break
    s = '-'.join(picked_words).lower() # join with hyphens, convert to lowercase
    if not s: # empty string unnacceptable
        return genRandomId(p_length=min(5,maxlen)) # for backwards compat., but also take in mind maxlen
    return s

def cleanupId(p_id=''):
    """
    DEPRECATED! Use  Use slugify(s)
    Slugifies/cleanups an id considered correctly formed in the begining
    """
    warn('cleanupId is deprecated. Use slugify(s) instead',
         DeprecationWarning, stacklevel=2)
    return slugify(p_id,1000,[])

def uniqueId(id,exists):
    """
    Returns an available id
     * `id`: a valid id - you can use slugify(s) to get one
     * `exists`: callback exists(id) returns True if id is already taken\
    (unavailable for use).

    """
    i = 1
    search_id = id
    while(exists(search_id)):
        search_id = '%s-%d' % (id, i)
        i += 1
    return search_id

def make_id(parent, temp_parent=None,
            id='', title='',
            prefix='', removelist=None):
    """
    Generates a valid unique id based on a suggested id, title or prefix
    The generated id is checked for uniqueness in the parent folder
    and if passed, in a second, 'temporary' folder

    Refactored to use the new slugify and uniqueId functions
    Does not strip common words out of id, prefix is appended a 5-digit no.
    """
    if prefix:
        # prefix implemented no-id-reuse in prev version, keeping it
        prefix = prefix + genRandomId(5)
    if id:
        assert(isinstance(id, basestring))
        gen_id = id
    else:
        gen_id = slugify(id or title or prefix, removelist=removelist)
    gen_id = strip_lead_trail(gen_id)

    if temp_parent:
        exists_fct = lambda c: (temp_parent._getOb(c,None) or
                               parent._getOb(c,None)) is not None
    else:
        exists_fct = lambda c: parent._getOb(c,None) is not None
    return uniqueId(gen_id, exists_fct)

def strip_lead_trail(name, lead=default_remove_lead,
                     trail=default_remove_trail):
    """ Function to remove unwanted leading and trailing character
        sequences from filenames (or strings in general)."""
    for str_lead in lead:
        if name[:len(str_lead)] == str_lead:
            name = strip_lead_trail(name[len(str_lead):], lead, trail)
    for str_trail in trail:
        if name[-len(str_trail):] == str_trail:
            name = strip_lead_trail(name[:-len(str_trail)], lead, trail)
    return name


def genRandomId(p_length=10, p_chars=string.digits):
    """Generate a random numeric id."""
    return ''.join([choice(p_chars) for i in range(p_length)])

def findDuplicates(objects, attributes):
    """Returns an iterator with the duplicate objects.

        Items with equal attributes are considered duplicated.
        @param objects: objects to test
        @type objects: iterator or sequence
        @param attributes: sequence of attributes that need to be equal to consider the objects duplicate
        @type attributes: sequence of strings
        @rtype: iterator
    """
    all_items = {}
    for item in objects:
        marker = tuple([getattr(item, attr) for attr in attributes]) # TODO Python 2.4: generator comprehension
        all_items.setdefault(marker, []).append(item)
    for items in all_items.values():
        if len(items) < 2:
            continue
        for item in items:
            yield item

def convertToList(s):
    """Convert to list"""
    if isinstance(s, tuple):
        s = list(s)
    elif not isinstance(s, list):
        s = [s]
    return s

def html2text(html, trim_length=512, ellipsis=False):
    """
    Strip all tags from ``html``. If ``trim_length`` is not None,
    limit the output length to ``trim_length`` characters.

    If the `ellipsis` flag is set to True, and `trim length` is not
    a false value (e.g. zero, None), then search for the nearest word
    boundary to the left, trim there, and insert an ellipsis ("...").
    """
    soup = BeautifulSoup(html)
    text = unescape_html_entities(''.join(soup.findAll(text=True))).strip()
    if trim_length and trim_length < len(text):
        text = text[:trim_length]
        if ellipsis:
            ELLIPSIS = u'\u2026'
            text = re.sub(r'(?<=\s)\S+$', ELLIPSIS, text)
    return text

def normalize_template(src):
    src = (src.strip().replace('\r', '')+'\n')
    if isinstance(src, unicode):
        src = src.encode('utf-8')
    return src

def html_diff(source, target):
    import difflib
    from cStringIO import StringIO
    lines = lambda s: StringIO(normalize_template(s)).readlines()
    html_escape_table = {'&': '&amp;', '<': '&lt;', '>': '&gt;',
            '"': '&quot;', "'": '&apos;', ' ': '&nbsp;', '\t': '&#09'}
    htmlquote = lambda s: "".join(html_escape_table.get(c, c) for c in s)
    output = StringIO()
    output.write('<div style="font-family: monospace;">')
    for line in difflib.unified_diff(lines(source), lines(target)):
        if line.startswith('+'):
            cls = 'line_added'
        elif line.startswith('-'):
            cls = 'line_removed'
        elif line.startswith('@@'):
            cls = 'line_heading'
        else:
            cls = 'line_normal'
        output.write('<div class="%s">%s</div>\n' % (cls, htmlquote(line)))
    output.write('</div>')
    return output.getvalue()

class list_utils:
    """Provides some interface to handle a list of ids: add/remove id from list"""

    def __init__(self):
        """Constructor"""
        pass

    def stripHTMLTags(self, s):
        """ Takes a text and removes the HTML tags leaving just plain text """
        strip_html_pattern = re.compile(r'<[^>]*>')
        plaintext = strip_html_pattern.sub(' ', s)
        plaintext = plaintext.replace('&nbsp;', ' ')
        return plaintext.replace('  ', ' ')

    def splitToList(self, s, separator=','):
        """Gets a comma separated string and returns a list"""
        if s is None:
            return []
        if not isinstance(s, (list, tuple, basestring)):
            raise ValueError("Invalid list %r" % s)
        if isinstance(s, basestring):
            s = s.split(separator)
        s = [x.strip() for x in s]
        return [x for x in s if x]

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

    def utRemoveLineInString(self, p_keyword, p_string):
        """ """
        l_str_lines = p_string.splitlines(1)
        l_str_refined = ''
        for ln in l_str_lines:
            if ln.find(p_keyword) != -1:
                l_str_lines.remove(ln)
        for st in l_str_lines:
            l_str_refined = l_str_refined + st
        return l_str_refined

    def utEliminateDuplicatesByURL(self, p_objects):
        """ eliminate duplicates from a list of objects """
        dict = {}
        for l_object in p_objects:
            dict[l_object.absolute_url()] = l_object
        return dict.values()

    def utEliminateDuplicateBrains(self, p_brains):
        """ eliminate duplicates from a list of brains """
        dict = {}
        for l_brain in p_brains:
            dict[l_brain.getPath()] = l_brain
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
    """
    Utility functions. All Naaya objects currently inherit from this class.
    """

    def __init__(self):
        """Constructor"""
        pass

    def splitTextByWords(self, text='', words=7):
        """ Split a text by given words

        Example:
        >>> text = 'this is a text to split in seven words'
        >>> print splitTextByWords(text)
        this is a text to split in ...
        """
        list_text = text.split(' ')
        if len(list_text) <= words:
            return text
        return ' '.join(list_text[:words]) + ' ...'

    def word_break(self, text='', insert="<wbr />", nchars=10):
        """ Insert a string (insert) every space or if a word length is bigger
        than given chars, every ${chars} characters.

        Example:
        >>> text = 'this is a bigwordwith_and-and.jpg'
        >>> print word_break(text)
        this is a bigwordwit<wbr />h_and-and.<wbr />jpg
        """
        list_text = text.split(' ')
        res = []
        for word in list_text:
            word = [word[i:i + nchars] for i in xrange(0, len(word), nchars)]
            word = insert.join(word)
            res.append(word)
        return ' '.join(res)

    def html2text(self, *args, **kwargs):
        return html2text(*args, **kwargs)

    #backwards compatibility
    def utStripAllHtmlTags(self, html):
        return self.html2text(html, trim_length=None)

    def getObjectPaginator(self, objects_list, num_per_page=50, orphans=-1):
        """ Returns objects_list in pages."""
        if orphans == -1:
            orphans = num_per_page * 20 / 100 # 20 %
        return ObjectPaginator(objects_list, num_per_page, orphans)

    def utGenObjectId(self, s, num_chars=80, removelist=None):
        """ deprecated, use utSlugify instead """
        warn('utGenObjectId is deprecated. Use utSlugify(s) instead',
             DeprecationWarning, stacklevel=2)
        return slugify(s,num_chars,removelist)

    def toAscii(self, *args, **kw):
        """ toAscii job now done by unidecode module"""
        return unidecode(*args, **kw)

    def parse_tags(self, tag_names):
        """ parse comma separated text """
        #find_tag_re = re.compile('[-\w]+')
        find_tag_re = re.compile('([^",]*)')
        return find_tag_re.findall(tag_names or '')

    def utGetROOT(self):
        """ get the ROOT object"""
        return self.unrestrictedTraverse(('',))

    def utGetObject(self, path=None, default=None):
        """ get an object by path """
        try: return self.unrestrictedTraverse(path, default)
        except: return None

    def utGenRandomId(self, *args, **kw):
        """See the genRandomId function"""
        return genRandomId(*args, **kw)

    def utGenerateUID(self, p_string=''):
        """ Generate an UID based on current time and a random string """
        if p_string == '': p_string = '%s%s' % (time.time(), self.utGenRandomId())
        return md5.new(p_string).hexdigest()

    def utCleanupId(self, p_id=''):
        """DEPRECATED! Use utSlugify(s)
        See the cleanupId function"""
        warn('utCleanupId is deprecated. Use utSlugify(s) instead',
             DeprecationWarning, stacklevel=2)
        return slugify(p_id,1000,[])

    def utSlugify(self, *args, **kw):
        """See slugify function"""
        return slugify(*args, **kw)

    def utCleanupProfileId(self, p_id=''):
        """ """
        if isinstance(p_id, unicode):
            x = p_id.encode('utf-8')
        else:
            x = str(p_id)
        TRANSMAP = string.maketrans('@', '_')
        return x.translate(TRANSMAP)

    def utValidateId(self, p_id=''):
        """."""
        try: checkValidId(self, p_id)
        except Exception, error:
            if str(error) != "('Empty or invalid id specified', '')":
                return [str(error)]
        return None

    def utConvertToList(self, *args, **kw):
        """see the convertToList function"""
        return convertToList(*args, **kw)

    def utConvertListToLines(self, values):
        """Takes a list of values and returns a value for a textarea control"""
        return '\r\n'.join(values)

    def utConvertLinesToList(self, value):
        """Takes a value from a textarea control and returns a list of values"""
        if type(value) == type([]):
            return value
        elif value == '':
            return []
        else:
            return [v for v in value.replace('\r', '').split('\n') if v != '']

    def utSplitSequence(self, seq, size):
        """
        Split up seq in pieces of size.
        """
        return [seq[i:i+size] for i in range(0, len(seq), size)]

    def utNewlinetoBr(self, p_string):
        #convert new lines to <br /> for html display
        return p_string.replace('\r', '').replace('\n', '<br />')

    def utListDifference(self, p_l1, p_l2):
        return list(set(p_l1) - set(p_l2))

    def utListIntersection(self, p_l1, p_l2):
        return list(set(p_l1) & set(p_l2))

    def utJoinToString(self, something, separator='/'):
        """Get a list [value1, values...], and returns a string like value1<separator>value2..."""
        return separator.join(self.utConvertToList(something))

    def _ut_getattr(self, obj, attr):
        """ Custom getattr used for utSortObjsListByAttr """
        return getattr(obj, attr, None)

    def utSortObjsListByAttr(self, p_list, p_attr, p_desc=1):
        """Sort a list of objects by an attribute values"""

        def sort_key(obj):
            attr = getattr(obj, p_attr, None)
            if isinstance(attr, basestring):
                return force_to_unicode(attr)
            else:
                return attr
        return sorted(p_list, key=sort_key, reverse=bool(p_desc))

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

    def utLinkifyURLs(self, string):
        def replace(match):
            txt = match.group('uri').replace('&amp;', '&')
            #if txt.startswith('http://'):
            if match.group('uri_proto'):
                uri = txt
            else:
                uri = 'http://' + txt
            return '<a href="%s">%s</a>' % (uri, txt)


        initial_lookbehind = r'(?<![\d\w\-])'
        host_component = r'[\w\d\-]+'
        host_port = r'\:\d+'
        path = r'/[^\s]*'
        get_params = r'\?[\w\d\=\%\&\;\-]*(?<!;)'

        regexp = r'(?P<uri>' \
                + initial_lookbehind \
                + r'((?P<uri_proto>\w+\://)|www\.)' \
                + host_component + r'(\.' + host_component + r')*' + r'('+ host_port + r')?' \
                + r'(' + path + r')?' \
                + r'(' + get_params + r')?' \
            + r')'

        return re.sub(regexp, replace, string)

    def utStringEscape(self, p_string):
        """ Escape a string/unicode
        """
        if isinstance(p_string, unicode):
            p_string = p_string.encode('unicode_escape')
        return p_string.encode('string_escape')

    def utUrlEncode(self, p_string, qtype=0):
        """Encode a string using url_quote"""
        if qtype:
            return p_string
        else:
            return url_quote(self.utToUtf8(p_string))

    def utURLEncodeList(self, list):
        return [self.utUrlEncode(l) for l in list]

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
          - replace \n with <br />"""
        l_tmp = self.utHtmlEncode(p_string)
        l_tmp = l_tmp.replace('\n', '<br />')
        return l_tmp

    def utXmlEncode(self, p_string):
        """Encode some special chars"""
        if isinstance(p_string, unicode): l_tmp = self.utToUtf8(p_string)
        else: l_tmp = str(p_string)
        l_tmp = l_tmp.replace('&', '&amp;')
        l_tmp = l_tmp.replace('<', '&lt;')
        l_tmp = l_tmp.replace('"', '&quot;')
        l_tmp = l_tmp.replace('\'', '&apos;')
        l_tmp = l_tmp.replace('>', '&gt;')
        return l_tmp

    def utJavaScriptEncode(self, s):
        """Encode a string for javascript processing"""
        regex = re.compile(r'([\]/.*+?<>|()[{}\\])')
        return regex.sub(r'', s)

    def utJsEncode(self, p_string):
        """Encode a string for javascript processing"""
        l_tmp = str(p_string)
        l_tmp = l_tmp.replace('\\', '\\\\')
        l_tmp = l_tmp.replace('\'', '\\\'')
        l_tmp = l_tmp.replace('\"', '\\\"')
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
        """ transform a file size in KB """
        return int(p_size/1024 + 1)

    def utShowSize(self, p_size):
        #Transform a file size in KB, MB ..
        l_bytes = float(p_size)
        l_type = ''
        l_res = ''
        if l_bytes >= 1000:
            l_bytes = l_bytes/1024
            l_type = 'KB'
            if l_bytes >= 1000:
                l_bytes = l_bytes/1024
                l_type = 'MB'
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
        """date is a DateTime or datetime object. This function returns a string 'dd month_name yyyy'"""
        try: return p_date.strftime('%d/%m/%Y')
        except: return ''

    # generic function, must be replaced for CHM and other sites !!!
    def utShowDateTime1(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy'"""
        try: return p_date.strftime('%d %b %Y')
        except: return ''

    def utShowCustom(self, p_date):
        """ """
        try: return p_date.strftime('%Y-%m-%d')
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
            if isinstance(p_start, DateTime):
                p_start = DT2dt(p_start)
            if isinstance(p_end, DateTime):
                p_end = DT2dt(p_end)
            sd, sm, sy = p_start.day, p_start.month, p_start.year
            ed, em, ey = p_end.day, p_end.month, p_end.year
            if sy == ey:    #same year
                if sm == em:    #same month
                    return '%s - %s %s' % (sd, p_end.strftime('%e %b'), sy)
                else:
                    return '%s - %s %s' % (p_start.strftime('%e %b'), p_end.strftime('%e %b'), sy)
            else:
                return '%s %s - %s %s' % (p_start.strftime('%e %b'), sy, p_end.strftime('%e %b'), ey)

    def utShowInterval(self, start_date, end_date, all_day):
        """Pretty print Products.NaayaCore.SchemaTool.widgets.interval.Interval
        """
        if isinstance(start_date, DateTime):
            start_date = DT2dt(start_date)
        if isinstance(end_date, DateTime):
            end_date = D2dt(end_date)
        if all_day:
            if start_date == end_date:
                return self.utShowDateTime(start_date)
            else:
                return self.utShowDateTimePeriod(start_date, end_date)
        else:
             return ('%s, %s - %s, %s' %
                     (self.utShowDateTime(start_date),
                      start_date.strftime('%H:%M'),
                      self.utShowDateTime(end_date),
                      end_date.strftime('%H:%M'))
                    )

    def utShowTime(self, date):
        if date:
            return date.strftime('%H:%M')
        else:
            return ''

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
        """ Formats datetime/DateTime like 'dd/mm/yyyy' """
        if p_date:
            return p_date.strftime(p_separator.join(("%d", "%m", "%Y")))
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
        return not p_str.strip()

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

    def parseValue(self, value):
        """ parse a value """
        if value.startswith('['):
            return eval(value)
        else:
            return value

    def utIsFloat(self, p_data, positive=1):
        """Test if the p_data parameter is float"""
        if p_data:
            try:
                p_data = float(p_data)
                if positive:
                    return p_data >= 0
                else:
                    return 1
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
            if isinstance(filename, unicode):
                filename = filename.encode('utf-8')
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

#CUSTOM FUNCTIONS
# arnaud.reveillon@naturalsciences.be

    def utSetBodyClass(self,url):
        if url.count('/admin_')>0 or url.count('/PhotoArchive')>0 or url.count('/GraphicsArchive')>0:
            bodyClass=('admin')
        elif url.count('edit_html')>0:
            bodyClass=('edit')
        elif url.count('add_html')>0:
            bodyClass=('add')
        try:return bodyClass
        except:return ''

    def utCustomShowDateTime(self, p_date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy'"""
        try: return p_date.strftime('%d.%m.%Y')
        except: return ''

    def utCustomShowWordedDate(self, p_date, p_language):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy'"""
        nd=p_date.strftime('%d')
        nm=p_date.strftime('%m')
        ny=p_date.strftime('%Y')

        if nm=='01':
            if p_language=='fr-BE':
                return nd+' janvier '+ny
            elif p_language=='nl-BE':
                return nd+' januari '+ny
            else:
                return nd+' January '+ny
        elif nm=='02':
            if p_language=='fr-BE':
                return nd+' f&eacute;vrier '+ny
            elif p_language=='nl-BE':
                return nd+' februari '+ny
            else:
                return nd+' February '+ny
        elif nm=='03':
            if p_language=='fr-BE':
                return nd+' mars '+ny
            elif p_language=='nl-BE':
                return nd+' maart '+ny
            else:
                return nd+' March '+ny
        elif nm=='04':
            if p_language=='fr-BE':
                return nd+' avril '+ny
            elif p_language=='nl-BE':
                return nd+' april '+ny
            else:
                return nd+' April '+ny
        elif nm=='05':
            if p_language=='fr-BE':
                return nd+' mai '+ny
            elif p_language=='nl-BE':
                return nd+' mei '+ny
            else:
                return nd+' May '+ny
        elif nm=='06':
            if p_language=='fr-BE':
                return nd+' juin '+ny
            elif p_language=='nl-BE':
                return nd+' juni '+ny
            else:
                return nd+' June '+ny
        elif nm=='07':
            if p_language=='fr-BE':
                return nd+' juillet '+ny
            elif p_language=='nl-BE':
                return nd+' juli '+ny
            else:
                return nd+' July '+ny
        elif nm=='08':
            if p_language=='fr-BE':
                return nd+' ao&ucirc;t '+ny
            elif p_language=='nl-BE':
                return nd+' augustus '+ny
            else:
                return nd+' August '+ny
        elif nm=='09':
            if p_language=='fr-BE':
                return nd+' septembre '+ny
            elif p_language=='nl-BE':
                return nd+' september '+ny
            else:
                return nd+' September '+ny
        elif nm=='10':
            if p_language=='fr-BE':
                return nd+' octobre '+ny
            elif p_language=='nl-BE':
                return nd+' oktober '+ny
            else:
                return nd+' October '+ny
        elif nm=='11':
            if p_language=='fr-BE':
                return nd+' novembre '+ny
            elif p_language=='nl-BE':
                return nd+' november '+ny
            else:
                return nd+' November '+ny
        elif nm=='12':
            if p_language=='fr-BE':
                return nd+' d&eacute;cembre '+ny
            elif p_language=='nl-BE':
                return nd+' december '+ny
            else:
                return nd+' December '+ny
        else:
            return nm

    # Easy access to urlencode method
    def utUrlLibEncode(self, query, doseq=1):
        return urlencode(query, doseq)

    def utRemoveLineInString(self, p_keyword, p_string):
        """ """
        l_str_lines = p_string.splitlines(1)
        l_str_refined = ''
        for ln in l_str_lines:
            if ln.find(p_keyword) != -1:
                l_str_lines.remove(ln)
        for st in l_str_lines:
            l_str_refined = l_str_refined + st
        return l_str_refined

    def utStripMSWordUTF8(self, s):
        """ replace MSWord characters """
        s = s.replace('\\xe2\\x80\\xa6', '...') #ellipsis
        s = s.replace('\\xe2\\x80\\x93', '-')   #long dash
        s = s.replace('\\xe2\\x80\\x94', '-')   #long dash
        s = s.replace('\\xe2\\x80\\x98', '\'')  #single quote opening
        s = s.replace('\\xe2\\x80\\x99', '\'')  #single quote closing
        s = s.replace('\\xe2\\x80\\x9c', '"')  #single quote closing
        s = s.replace('\\xe2\\x80\\x9d', '"')  #single quote closing
        s = s.replace('\\xe2\\x80\\xa2', '*')  #dot used for bullet points
        return s

    def utHexColors(self, lang):
        """ returns a hex color code to be used as language color in edit forms """
        colors = ['DEE6FF', 'F8FFDE', 'FFE6DE', 'DEFFE0', 'DEF2FF']
        langs = [x for x in self.gl_get_languages()]
        if lang in langs:
            l_in = langs.index(lang)%len(colors)
        else:
            l_in = -1
        return '#%s' % colors[l_in]

#END OF CUSTOM FUNCTIONS

class spreadsheet_file:

    def __init__(self, data, dialect='excel'):
        self.fname = tempfile.mktemp()
        writer = csv.writer(open(self.fname,'wb'), dialect)
        for row in data:
            writer.writerow(row)

    def __str__(self): return self.fname
    __repr__ = __str__

    def __del__(self):
        os.unlink(self.fname)

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

class InvalidStringError(Exception):
    """ Invalid String Exception """
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return 'Invalid string: %s' % self.msg

def object2string(obj):
    """ Pickle obj and base64 encode. Use string2object to recover it.
    """
    buff = StringIO()
    pickle.dump(obj, buff)
    return base64.encodestring(buff.getvalue())

def string2object(string):
    """ Revert object2string.
    """
    buff = StringIO()
    # base64 decode string
    try:
        text = base64.decodestring(string)
    except base64.binascii.Error:
        raise InvalidStringError(string)
    else:
        buff.write(text)
        buff.seek(0)
    # Convert to object
    try:
        obj = pickle.load(buff)
    except IndexError:
        raise InvalidStringError(string)
    else:
        return obj


class vcard_file:
    """ Container class for vcard data. Needed for zip export """
    def __init__(self, id, data):
        self.id = '%s.vcf' % (id, )
        self.data = data

    def getZipData(self):
        if isinstance(self.data, unicode):
            return self.data.deocde('utf-8')
        else:
            return self.data

    def get_size(self):
        return len(self.data)

def get_nsmap(namespaces):
    nsmap = {}
    for n in namespaces:
        if n.prefix != '':
            nsmap[n.prefix] = n.value
        else:
            nsmap[None] = n.value
    return nsmap

def rss_item_for_channel(channel):
    s = channel.getSite()
    namespaces = channel.getNamespaceItemsList()
    nsmap = get_nsmap(namespaces)
    rdf_namespace = nsmap['rdf']
    dc_namespace = nsmap['dc']
    Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
    E = ElementMaker(None, nsmap=nsmap)
    item = E.item(
         {'{%s}about'%rdf_namespace : channel.absolute_url()},
         E.link(channel.absolute_url()),
         E.title(channel.title_or_id()),
         E.description(channel.description),
         Dc.title(channel.title_or_id()),
         Dc.description(channel.description),
         Dc.contributor(channel.contributor),
         Dc.language(channel.language),
         Dc.creator(channel.creator),
         Dc.publisher(channel.publisher),
         Dc.rights(channel.rights),
         Dc.type(channel.get_channeltype_title(channel.type)),
         Dc.format('text/xml'),
         Dc.source(channel.publisher)
        )
    return item

def rss_channel_for_channel(channel, lang):
    s = channel.getSite()
    namespaces = channel.getNamespaceItemsList()
    nsmap = get_nsmap(namespaces)
    rdf_namespace = nsmap['rdf']
    dc_namespace = nsmap['dc']
    Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
    E = ElementMaker(None, nsmap=nsmap)
    channel = E.channel(
            E.title(channel.title),
            E.link(s.absolute_url()),
            E.description(channel.description),
            Dc.description(channel.description),
            Dc.identifier(s.absolute_url()),
            Dc.date(channel.utShowFullDateTimeHTML(channel.utGetTodayDate())),
            Dc.publisher(s.getLocalProperty('publisher', lang)),
            Dc.creator(s.getLocalProperty('creator', lang)),
            Dc.subject(s.getLocalProperty('site_title', lang)),
            Dc.subject(s.getLocalProperty('site_subtitle', lang)),
            Dc.language(lang),
            Dc.rights(s.getLocalProperty('rights', lang)),
            Dc.type(channel.type),
            Dc.source(s.getLocalProperty('publisher', lang)),
            E.items(),
           {'{%s}about'%rdf_namespace : s.absolute_url()}
          )
    return channel
