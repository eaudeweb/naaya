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
import string
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports
from Products.Naaya.constants import *
from Products.NaayaContent import *

class config_struct:
    def __init__(self):
        self.urls = None

class urls_struct:
    def __init__(self):
        self.entries = []

class entry_struct:
    def __init__(self, meta_type, property):
        self.meta_type = meta_type
        self.property = property

class saxstack_struct:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

class config_handler(ContentHandler):
    """ """

    def __init__(self):
        self.root = None
        self.stack = []

    def startElement(self, name, attrs):
        """ """
        if name == 'config':
            obj = config_struct()
            stackObj = saxstack_struct('config', obj)
            self.stack.append(stackObj)
        elif name == 'urls':
            obj = urls_struct()
            stackObj = saxstack_struct('urls', obj)
            self.stack.append(stackObj)
        elif name == 'entry':
            obj = entry_struct(attrs['meta_type'].encode('utf-8'), attrs['property'].encode('utf-8'))
            stackObj = saxstack_struct('entry', obj)
            self.stack.append(stackObj)

    def endElement(self, name):
        """ """
        if name == 'config':
            self.root = self.stack[-1].obj
            self.stack.pop()
        elif name == 'urls':
            self.stack[-2].obj.urls = self.stack[-1].obj
            self.stack.pop()
        elif name == 'entry':
            self.stack[-2].obj.entries.append(self.stack[-1].obj)
            self.stack.pop()

    def characters(self, content):
        if len(self.stack) > 0:
            self.stack[-1].content += content.strip(' \t')

class config_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parse(self, p_content):
        """ """
        l_handler = config_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        try:
            l_parser.parse(l_inpsrc)
            return (l_handler, '')
        except Exception, error:
            return (None, error)
