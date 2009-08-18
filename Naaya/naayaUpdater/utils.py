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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alec Ghica, Eau de Web
# Cornel Nitu, Eau de Web

import sys
import sha

def convertToList(data):
    """ convert to list """
    res = []
    add_res = res.append
    if type(data) == type([]):
        res.extend(data)
    else:
        [add_res(k.strip()) for k in data.split(',')]
    return res

def minDate(a,b):
    """.compare dates """
    if a < b: return a
    else:     return b

def isUnixLike():
    """ find if the operating system is Unix-like"""
    if sys.platform == 'win32':
        return False
    return True

def convertLinesToList(value):
    """ takes a value from a textarea control and returns a list of values """
    if type(value) == type([]): return value
    elif value == '': return []
    else:
        values = []
        for v in value.split('\n'):
            if v != '': values.append(v.replace('\r', ''))
    return values

def readFile(p_path, p_flag='r'):
    """ """
    return open(p_path, p_flag).read()

def create_signature(s):
    if s is not None:
        m = sha.new(s)
        res = m.hexdigest()
        m = None
        return res
    else:
        return s

def html_decode(s):
    """Decode some special chars"""
    if isinstance(s, unicode): buf = s.encode('utf-8')
    else: buf = str(s)
    buf = buf.replace('&amp;', '&')
    buf = buf.replace('&lt;', '<')
    buf = buf.replace('&quot;', '"')
    buf = buf.replace('&apos;', '\'')
    buf = buf.replace('&gt;', '>')
    return buf

def physical_path(ob):
    return '/'.join(ob.getPhysicalPath()[1:])
