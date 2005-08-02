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
#
#
#
#$Id: ini_portal_parser.py 2464 2004-11-04 13:28:49Z finrocvs $

#Python imports
import string
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports

class content_struct:
    def __init__(self, maintopics):
        self.maintopics = maintopics
        self.localchannels = []
        self.remotechannels = []
        self.linkslists = []
        self.folders = []

class localchannel_struct:
    def __init__(self, id, title, description, language, type, objmetatype, numberofitems):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.objmetatype = objmetatype
        self.numberofitems = numberofitems

class remotechannel_struct:
    def __init__(self, id, title, url, numbershownitems):
        self.id = id
        self.title = title
        self.url = url
        self.numbershownitems = numbershownitems

class linkslist_struct:
    def __init__(self, id, title, portlet):
        self.id = id
        self.title = title
        self.portlet = portlet
        self.links = []

class link_struct:
    def __init__(self, id, title, description, url, relative, permission, order):
        self.id = id
        self.title = title
        self.description = description
        self.url = url
        self.relative = relative
        self.permission = permission
        self.order = order

class folder_struct:
    def __init__(self, id, title, description, coverage, keywords, publicinterface, maintainer_email, sortorder, meta_types):
        self.id = id
        self.title = title
        self.description = description
        self.coverage = coverage
        self.keywords = keywords
        self.publicinterface = publicinterface
        self.maintainer_email = maintainer_email
        self.sortorder = sortorder
        self.meta_types = meta_types
        self.folders = []
        self.items = []
        self.index_html = None

class saxstack_struct:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

class portal_handler(ContentHandler):
    """ """

    def __init__(self):
        self.root = None
        self.stack = []

    def startElement(self, name, attrs):
        """ """
        if name == 'content':
            obj = content_struct(attrs['maintopics'].encode('utf-8'))
            stackObj = saxstack_struct('content', obj)
            self.stack.append(stackObj)
        elif name == 'localchannel':
            obj = localchannel_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['language'].encode('utf-8'), attrs['type'].encode('utf-8'), attrs['objmetatype'].encode('utf-8'), attrs['numberofitems'].encode('utf-8'))
            stackObj = saxstack_struct('localchannel', obj)
            self.stack.append(stackObj)
        elif name == 'remotechannel':
            obj = remotechannel_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['url'].encode('utf-8'), attrs['numbershownitems'].encode('utf-8'))
            stackObj = saxstack_struct('remotechannel', obj)
            self.stack.append(stackObj)
        elif name == 'linkslist':
            obj = linkslist_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['portlet'].encode('utf-8'))
            stackObj = saxstack_struct('linkslist', obj)
            self.stack.append(stackObj)
        elif name == 'link':
            if len(self.stack) >=2:
                obj = link_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['url'].encode('utf-8'), attrs['relative'].encode('utf-8'), attrs['permission'].encode('utf-8'), attrs['order'].encode('utf-8'))
                stackObj = saxstack_struct('link', obj)
                self.stack.append(stackObj)
        elif name == 'folder':
            obj = folder_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['coverage'].encode('utf-8'), attrs['keywords'].encode('utf-8'), attrs['publicinterface'].encode('utf-8'), attrs['maintainer_email'].encode('utf-8'), attrs['sortorder'].encode('utf-8'), attrs['meta_types'].encode('utf-8'))
            stackObj = saxstack_struct('folder', obj)
            self.stack.append(stackObj)

    def endElement(self, name):
        """ """
        if name == 'content':
            self.root = self.stack[-1].obj
            self.stack.pop()
        elif name == 'localchannel':
            self.stack[-2].obj.localchannels.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'remotechannel':
            self.stack[-2].obj.remotechannels.append(self.stack[-1].obj)
            self.stack.pop()
        if name == 'linkslist':
            self.stack[-2].obj.linkslists.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'link':
            self.stack[-2].obj.links.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'folder':
            self.stack[-1].obj.index_html = self.stack[-1].content.encode('utf-8')
            self.stack[-2].obj.folders.append(self.stack[-1].obj)
            self.stack.pop()

    def characters(self, content):
        if len(self.stack) > 0:
            self.stack[-1].content += content.strip(' \t')

class ini_content_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parseContent(self, p_content):
        """ """
        l_handler = portal_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        #try:
        l_parser.parse(l_inpsrc)
        return (l_handler, '')
        #except Exception, error:
        #    return (None, error)
