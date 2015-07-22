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
# The Original Code is HelpDeskAgent version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Dragos Chirila, Finsiel Romania

# Generic functions

import re, string,types,time
from random import choice
from Products.PythonScripts.standard import url_quote, html_quote
from DateTime import DateTime

def GenRandonName(length=10, chars=string.letters + string.digits + ' '):
    """Generate a rondom name."""
    return ''.join([choice(chars) for i in range(length)])

def GenRandomId(length=10, chars=string.letters + string.digits):
    """Generate a random id."""
    return ''.join([choice(chars) for i in range(length)])

def GenRandomKey(length=10, chars=string.digits):
    """Generate a random numeric key."""
    return ''.join([choice(chars) for i in range(length)])

def ConvertToList(something):
    """Convert to list"""
    ret = something
    if type(something) is type(''):
        ret = [something]
    return ret

def addObjectAction(REQUEST=None):
    """Check if adding an object"""
    res = 0
    if REQUEST:
        res = REQUEST.has_key('add')
    return res

def updateObjectAction(REQUEST=None):
    """Check if updating an object"""
    res = 0
    if REQUEST:
        res = REQUEST.has_key('update')
    return res

def deleteObjectAction(REQUEST=None):
    """Check if deleting an object"""
    res = 0
    if REQUEST:
        res = REQUEST.has_key('delete')
    return res

def addIssue(REQUEST=None):
    res = 0
    if REQUEST:
        res = REQUEST.has_key('addIssue')
    return res

def addIssueQuick(REQUEST=None):
    res = 0
    if REQUEST:
        res = REQUEST.has_key('addIssueQuick')
    return res

def setFormError(req, key, msg):
    req.set('FORM_ERROR', 1)
    req.set('FORM_ERROR_' + key, msg)
    return req


#####################
# DATE TIME methods #
#####################
def FormatDateToString(date):
    """Gets a DateTime object and returns a string like dd/mm/yyyy"""
    if type(date) is types.TupleType:
        date = DateTime(time.mktime(date))
    return date.strftime("%d/%m/%Y")

def FormatDateTimeToString(date):
    """Gets a DateTime object and returns a string like dd/mm/yyyy hh:mm:ss"""
    if type(date) is types.TupleType:
        date = DateTime(time.mktime(date))
    return date.strftime("%d/%m/%Y %H:%M:%S")


def FormatDateByModel(date, model):
    """Gets a DateTime object and return a string"""
    if type(date) is types.TupleType:
        date = DateTime(time.mktime(date))
    return date.strftime(model)


#############
# ENCODING  #
#############
def HTMLEncode(str):
    """Encode a string using html_quote"""
    return html_quote(str)

def URLEncode(str):
    """Encode a string using url_encode"""
    return url_quote(str)

def TEXTAREAEncode(str):
    """Encode a string (from a textarea control):
                - HTMLEncode str
                - replace \n with <br />"""
    buf = str
    buf = HTMLEncode(buf)
    buf = ParseStringForURL(buf)
    buf = string.replace(buf, '\n', '<br />')
    return buf


###########
# EMAILS  #
###########
def BuildEmailList(emaillist):
    """Build a string with all emails"""
    if len(emaillist)>0:
        return '<' + string.join(emaillist, '>,\n<') + '>'
    else:
        return ''

def ParseStringForURL(text):
    """ Parses a string and if any url are found then <a > ..</a> is created """
    urls = parseUrls(text)
    for url in urls:
        if len(url)>50: buf = '%s..' % url[:50]
        else: buf = url
        text = text.replace(url, '<a href="%s" target="_blank">%s</a>' % (url, buf))
    return text

def parseUrls(text):
    """ Given a text string, returns all the urls we can find in it. """
    urls = '(?: %s)' % '|'.join("http https telnet gopher file wais ftp".split())
    ltrs = r'\w'
    gunk = r'/#~:.?+=&%@!\-'
    punc = r'.:?\-'
    any = "%(ltrs)s%(gunk)s%(punc)s" % { 'ltrs':ltrs, 'gunk':gunk, 'punc':punc}
    url = r'\b%(urls)s:[%(any)s]+?(?=[%(punc)s]*(?:   [^%(any)s]|$))' % {'urls':urls, 'any':any, 'punc':punc}
    url_re = re.compile(url, re.VERBOSE | re.MULTILINE)
    return url_re.findall(text)
