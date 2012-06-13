import string
import operator
import datetime
import re

import transaction
from zope import interface, schema

url_pattern = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
bad_chars = '!@#$%\\/:"*?<>| ,+&;\'()[]{}\xC4\xC5\xC1\xC0\xC2\xC3' \
          '\xE4\xE5\xE1\xE0\xE2\xE3\xC7\xE7\xC9\xC8\xCA\xCB' \
          '\xC6\xE9\xE8\xEA\xEB\xE6\xCD\xCC\xCE\xCF\xED\xEC' \
          '\xEE\xEF\xD1\xF1\xD6\xD3\xD2\xD4\xD5\xD8\xF6\xF3' \
          '\xF2\xF4\xF5\xF8\x8A\x9A\xDF\xDC\xDA\xD9\xDB\xFC' \
          '\xFA\xF9\xFB\xDD\x9F\xFD\xFF\x8E\x9E'

good_chars= '__________________________AAAAAA' \
          'aaaaaaCcEEEE' \
          'EeeeeeIIIIii' \
          'iiNnOOOOOOoo' \
          'ooooSssUUUUu' \
          'uuuYYyyZz'

TRANSMAP = string.maketrans(bad_chars, good_chars)

def processId(p_id):
    """ Return a valid id """
    if isinstance(p_id, unicode): x = p_id.encode('utf-8')
    else: x = str(p_id)
    x = x.strip()
    x = x.translate(TRANSMAP)
    if x[0] == '_': x = x[1:]
    return x

def latin1_to_ascii (unicrap):
    """This takes a UNICODE string and replaces Latin-1 characters with
    something equivalent in 7-bit ASCII. It returns a plain ASCII string.
    This function makes a best effort to convert Latin-1 characters into
    ASCII equivalents. It does not just strip out the Latin-1 characters.
    All characters in the standard 7-bit ASCII range are preserved.
    In the 8th bit range all the Latin-1 accented letters are converted
    to unaccented equivalents. Most symbol characters are converted to
    something meaningful. Anything not converted is deleted.
    """
    xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
           0xc6:'Ae', 0xc7:'C',
           0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
           0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
           0xd0:'Th', 0xd1:'N',
           0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
           0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
           0xdd:'Y', 0xde:'th', 0xdf:'ss',
           0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
           0xe6:'ae', 0xe7:'c',
           0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
           0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
           0xf0:'th', 0xf1:'n',
           0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
           0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
           0xfd:'y', 0xfe:'th', 0xff:'y',
           0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
           0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
           0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
           0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
           0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
           0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
           0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
           0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
           0xd7:'*', 0xf7:'/'
           }

    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += str(i)
    return r

def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_unicode, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int, long, datetime.datetime, datetime.date, datetime.time, float)):
        return s
    try:
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), encoding, errors)
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        # error log
        pass
    return s
space_sub = re.compile('[\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\x09|\x10'
                       '|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x0A|\x0B'
                       '|\x0C|\x0D|\x0E|\x0F|\x1A|\x1B|\x1C|\x1D|\x1E|\x1F|\x7F'
                       '|\x13|\xc2\x80|\xc2\x81|\xc2\x82|\xc2\x83|\xc2\x84'
                       '|\xc2\x85|\xc2\x86|\xc2\x87|\xc2\x88|\xc2\x89|\xc2\x8a'
                       '|\xc2\x8b|\xc2\x8c|\xc2\x8d|\xc2\x8e|\xc2\x8f|\xc2\x90'
                       '|\xc2\x91|\xc2\x92|\xc2\x93|\xc2\x94|\xc2\x95|\xc2\x96'
                       '|\xc2\x97|\xc2\x98|\xc2\x99|\xc2\x9a|\xc2\x9b|\xc2\x9c'
                       '|\xc2\x9d|\xc2\x9e|\xc2\x9f]',
                       re.IGNORECASE)
newline_sub = re.compile('[\x0A|\x1F|\x0D]', re.IGNORECASE)
tab_sub = re.compile('[\x09]', re.IGNORECASE)

def clean_xml(str):
    """Clean null and control chars"""
    str = re.sub(space_sub, " ", str)
    str = re.sub(newline_sub, "\n", str)
    return re.sub(tab_sub, "\t", str)

def utConvertListToLines(values):
    """Takes a list of values and returns a value for a textarea control"""
    if len(values) == 0: return ''
    else: return '\r\n'.join(values)

def utConvertLinesToList(value):
    """Takes a value from a textarea control and returns a list of values"""
    if type(value) == type([]): return value
    elif value == '': return []
    else:
        values = []
        for v in value.split('\r\n'):
            if v != '': values.append(v)
    return values

def utSortDictsListByKey(p_list, p_key, p_desc=1):
        """Sort a list of objects by an item values"""
        l_len = len(p_list)
        l_temp = map(None, map(lambda x, y: x[y], p_list, (p_key,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc:
            l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)

def DT2dt(date):
    """Convert Zope's DateTime to Python's datetime
    Stolen from Plone-2.1.4/ATContentTypes/utils.py
    """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    return datetime.datetime(*args)

def create_object(self, klass, id):
    """ Try to create an object """
    id = processId(id)
    ob = klass()
    ob.id = id
    self._setObject(id, ob)
    return self._getOb(id)

def process_form(ob, schema_interface, form_data):
    """ Validate the date, save it if valid or abort transaction if not.
    """
    try:
        schema_fields = schema.getFields(schema_interface)
        for schema_field_name, schema_field_ob in schema_fields.items():
            schema_field_ob.validate(form_data.get(schema_field_name))
            schema_field_ob = schema_field_ob.bind(ob)
            if form_data.has_key(schema_field_name) or \
                getattr(schema_field_ob, 'update', True):
                setattr(ob, schema_field_name, form_data.get(schema_field_name,
                                                schema_field_ob.default))
    except Exception, e:
        transaction.abort()
        raise Exception(schema_field_name + ' ' +  str(e))

class DictDiffer(object):
    """ Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values

    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = (set(current_dict.keys()),
                                           set(past_dict.keys()))
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])

class ListDictDiffer(object):
    """ Calculate the difference between two lists of dictionaries:

    """

    def __init__(self, current, past, ignore_keys):
        self.current = self._filter(current, ignore_keys)
        self.past = self._filter(past, ignore_keys)

    def _filter(self, _list, ignore_keys):
        return [dict(filter(lambda k: k[0] not in ignore_keys, x.items()))
                for x in _list]

    def added(self):
        return [d for d in self.current if d not in self.past]

    def removed(self):
        """ Return the index that was removed """
        return [d for d in self.past if d not in self.current]

    def removed_index(self):
        """ Return the index that was removed """
        return [self.past.index(d) for d in self.past if d not in self.current]

class Empty:
    """ """
