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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports
import string
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports

class profilemeta_struct:
    def __init__(self):
        self.properties = []

class property_struct:
    def __init__(self, id, value, type):
        self.id = id
        self.value = value
        self.type = type

class saxstack_struct:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

class profilemeta_handler(ContentHandler):
    """ """

    def __init__(self):
        self.root = None
        self.stack = []

    def startElement(self, name, attrs):
        """ """
        if name == 'profilemeta':
            obj = profilemeta_struct()
            stackObj = saxstack_struct('profilemeta', obj)
            self.stack.append(stackObj)
        elif name == 'property':
            obj = property_struct(attrs['id'].encode('utf-8'), attrs['value'].encode('utf-8'), attrs['type'].encode('utf-8'))
            stackObj = saxstack_struct('property', obj)
            self.stack.append(stackObj)

    def endElement(self, name):
        """ """
        if name == 'profilemeta':
            self.root = self.stack[-1].obj
            self.stack.pop()
        elif name == 'property':
            self.stack[-2].obj.properties.append(self.stack[-1].obj)
            self.stack.pop()

    def characters(self, content):
        if len(self.stack) > 0:
            self.stack[-1].content += content.strip(' \t')

class profilemeta_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parse(self, p_content):
        """ """
        l_handler = profilemeta_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        try:
            l_parser.parse(l_inpsrc)
            return (l_handler, '')
        except Exception, error:
            return (None, error)
