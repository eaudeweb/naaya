# -*- coding: utf8 -*-
#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "EWGeoMap"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania and Eau de Web 
#are Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#        Bogdan Grama (Finsiel Romania)
#        Iulian Iuga (Finsiel Romania)
#  Porting to Naaya: 
#        Cornel Nitu (Eau de Web)


__doc__ = """
utils module.
"""

import os , math
import tempfile
import time
from os.path import join
from urllib import FancyURLopener

from constants import *

def utOpen(file):
    # Open file
    if 'http' in file:
        opener = FancyURLopener()
        f = opener.open(file)
    else:
        f = open(file,'rb+')
    return f

def utGMLEncode(p_str, p_str_enc):
    # Giving a string and an encoding, returns the string encoded to UTF-8
    # If no encoding is provided it will assume as input encoding UTF-8 
    # Also special characters that might appear in GML files are escaped
    if p_str_enc == '':
        l_tmp = unicode(str(p_str), errors='replace')
    else:
         l_tmp = unicode(str(p_str),'%s' % p_str_enc, errors='replace')
    l_tmp = l_tmp.encode('utf8', 'replace')
    #XML entities
    l_tmp = l_tmp.replace('&', '&amp;')
    l_tmp = l_tmp.replace('<', '&lt;')
    l_tmp = l_tmp.replace('"', '&quot;')
    l_tmp = l_tmp.replace('\'', '&apos;')
    l_tmp = l_tmp.replace('>', '&gt;')

    #TODO: replaced brocken characters
    #Microsoft Word entities
    l_tmp = l_tmp.replace('—', '-')
    l_tmp = l_tmp.replace('–', '-')
    l_tmp = l_tmp.replace('‘', "'")
    l_tmp = l_tmp.replace('’', "'")
    l_tmp = l_tmp.replace(' ', " ")
    l_tmp = l_tmp.replace('´', "'")
    l_tmp = l_tmp.replace('“', '&quot;')
    l_tmp = l_tmp.replace('”', '&quot;')
    l_tmp = l_tmp.replace('§', "-")
    l_tmp = l_tmp.replace('¤', " ")
    l_tmp = l_tmp.replace('«', "&quot;")
    l_tmp = l_tmp.replace('»', "&quot;")
    l_tmp = l_tmp.replace('…', "...")
    l_tmp = l_tmp.replace('•', "* ")

    return l_tmp

def utf8Encode(p_str):
    """ zip Encodes a string to UTF-8 """
    return p_str.encode('utf8')