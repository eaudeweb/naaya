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

"""
This module contains the classes for parsing export Naaya XML files.
"""

#Python imports
from copy import deepcopy
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports

class export_struct:
    def __init__(self):
        self.objects = []

class object_struct:
    def __init__(self, id, meta_type, param, attrs):
        self.id = id
        self.meta_type = meta_type
        self.param = param
        self.attrs = attrs
        self.content = None
        self.properties = {}
        self.discussion = None
        self.objects = []

class item_struct:
    def __init__(self, attrs):
        self.attrs = attrs
        self.content = None

class property_struct:
    def __init__(self, name, lang):
        self.name = name
        self.lang = lang

class discussion_struct:
    def __init__(self):
        self.comments = []

class comment_struct:
    def __init__(self, id, title, body, author, date):
        self.id = id
        self.title = title
        self.body = body
        self.author = author
        self.date = date

class saxstack_struct:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

class import_handler(ContentHandler):
    """
    Implements the ContentHandler callback interface.
    """

    def __init__(self):
        """
        Initialize the I{stack} and I{root} variables.
        """
        self.root = None
        self.stack = []

    def startElement(self, name, attrs):
        """ """
        if name == 'export':
            obj = export_struct()
            stackObj = saxstack_struct('export', obj)
            self.stack.append(stackObj)
        elif name == 'ob':
            obj = object_struct(attrs['id'].encode('utf-8'),
                                attrs['meta_type'].encode('utf-8'),
                                attrs['param'].encode('utf-8'),
                                attrs)
            stackObj = saxstack_struct('ob', obj)
            self.stack.append(stackObj)
        elif name == 'discussion':
            obj = discussion_struct()
            stackObj = saxstack_struct('discussion', obj)
            self.stack.append(stackObj)
        elif name == 'comment':
            obj = comment_struct(attrs['id'].encode('utf-8'),
                                 attrs['title'], attrs['body'],
                                 attrs['author'], attrs['date'])
            stackObj = saxstack_struct('comment', obj)
            self.stack.append(stackObj)
        elif name == 'img':
            obj = object_struct(attrs['id'].encode('utf-8'),
                                'Image',
                                attrs['param'].encode('utf-8'),
                                attrs)
            stackObj = saxstack_struct('img', obj)
            self.stack.append(stackObj)
        elif name == 'file':
            obj = object_struct(attrs['id'].encode('utf-8'),
                                'File',
                                attrs['param'].encode('utf-8'),
                                attrs)
            stackObj = saxstack_struct('file', obj)
            self.stack.append(stackObj)
        elif name == 'template':
            obj = object_struct(attrs['id'].encode('utf-8'),
                                'Page Template',
                                attrs['param'].encode('utf-8'),
                                attrs)
            stackObj = saxstack_struct('template', obj)
            self.stack.append(stackObj)
        elif name == 'item':
            obj = item_struct(attrs)
            stackObj = saxstack_struct('item', obj)
            self.stack.append(stackObj)
        elif attrs.has_key('lang'):
            #multilingual property
            name = name.encode('utf-8')
            obj = property_struct(name, attrs['lang'].encode('utf-8'))
            stackObj = saxstack_struct('name', obj)
            self.stack.append(stackObj)
        else:
            pass

    def endElement(self, name):
        """ """
        if name == 'export':
            self.root = self.stack[-1].obj
            self.stack.pop()
        elif name == 'ob':
            self.stack[-1].obj.content = self.stack[-1].content.encode('utf-8')
            self.stack[-2].obj.objects.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'discussion':
            self.stack[-2].obj.discussion = self.stack[-1].obj
            self.stack.pop()
        elif name == 'comment':
            self.stack[-2].obj.comments.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'img':
            self.stack[-2].obj.objects.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'file':
            self.stack[-2].obj.objects.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'template':
            self.stack[-1].obj.content = self.stack[-1].content.encode('utf-8')
            self.stack[-2].obj.objects.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'item':
            self.stack[-1].obj.content = self.stack[-1].content.encode('utf-8')
            self.stack[-2].obj.objects.append(self.stack[-1].obj)
            self.stack.pop()
        elif isinstance(self.stack[-1].obj, property_struct):
            #multilingual property
            name, lang = self.stack[-1].obj.name, self.stack[-1].obj.lang
            content = self.stack[-1].content
            self.stack.pop()
            ob = self.stack[-1].obj
            if not ob.properties.has_key(name):
                ob.properties[name] = {}
            ob.properties[name][lang] = content
        else:
            pass

    def characters(self, content):
        if len(self.stack) > 0:
            self.stack[-1].content += content.strip(' ')

class import_parser:
    """
    Parses XML and returns the results.
    If the XML is not valid an error is signaled.
    """

    def parse(self, p_content):
        """
        Parses an XML.
        @param p_content: the content of an XML file
        @type p_content: string
        @return:
            - if an error occures a tuple (None, error) is returned.
            - if no error, then a tuple (handler, '') is returned. The data
            stored in the handler object will be imported in the current
            portal.
        """
        l_handler = import_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        try:
            l_parser.parse(l_inpsrc)
            return (l_handler, '')
        except Exception, error:
            return (None, error)
