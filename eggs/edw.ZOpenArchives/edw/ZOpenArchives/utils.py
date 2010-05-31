# -*- coding: utf-8 -*-

import string
import operator
import datetime

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
    """ Retourne un identifiant valide """
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
    """Convert Zope's DateTime to Pythons's datetime
    Stolen from Plone-2.1.4/ATContentTypes/utils.py
    """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    return datetime.datetime(*args)
