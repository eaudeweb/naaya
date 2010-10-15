import string
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

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
