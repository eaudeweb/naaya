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
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports

class export_struct:
    def __init__(self):
        self.objects = []

class object_struct:
    def __init__(self, id, meta_type, attrs):
        self.id = id
        self.meta_type = meta_type
        self.attrs = attrs
        self.objects = []

class saxstack_struct:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

class import_handler(ContentHandler):
    """ """

    def __init__(self):
        self.root = None
        self.stack = []

    def startElement(self, name, attrs):
        """ """
        if name == 'export':
            obj = export_struct()
            stackObj = saxstack_struct('export', obj)
            self.stack.append(stackObj)
        elif name == 'ob':
            obj = object_struct(attrs['id'].encode('utf-8'), attrs['meta_type'].encode('utf-8'), attrs)
            stackObj = saxstack_struct('ob', obj)
            self.stack.append(stackObj)
        else:
            pass

    def endElement(self, name):
        """ """
        if name == 'export':
            self.root = self.stack[-1].obj
            self.stack.pop()
        elif name == 'ob':
            self.stack[-2].obj.objects.append(self.stack[-1].obj)
            self.stack.pop()
        else:
            pass

class import_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parse(self, p_content):
        """ """
        l_handler = import_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        #try:
        l_parser.parse(l_inpsrc)
        #l_handler.testImportTree()
        return (l_handler, '')
        #except Exception, error:
        #    return (None, error)
