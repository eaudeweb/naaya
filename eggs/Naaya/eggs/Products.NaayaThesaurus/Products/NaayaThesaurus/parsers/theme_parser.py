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
# Ghica Alexandru, Finsiel Romania


from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO
from types import StringType

class theme_handler(ContentHandler):
    """ This is used to parse the theme file
    """

    RDF_ATTRS = ['xml:lang']

    def __init__(self):
        """ constructor """
        self.__body = {}
        self.__langcode = ''
        self.__name = ''
        self.__id = ''

    def getLanguage(self):
        return self.__langcode

    def getBody(self):
        return self.__body

    def setBody(self, key, value):
        self.__body[key] = value

    def startElement(self, name, attrs):
        if name == 'rdf:RDF':
            for elem in attrs.keys():
                elem = elem.encode('utf-8')
                if elem in self.RDF_ATTRS:
                    self.__langcode = attrs['xml:lang']

        if name == 'skos:Concept':
            self.__name = attrs['rdfs:label']
            self.__id = attrs['rdf:about']

    def endElement(self, name):
        if name == 'skos:Concept':
            self.setBody(self.__id, {'id':self.__id,
                                     'name':self.__name})

class theme_parser:
    """ class for parse theme files """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        """ """
        chandler = theme_handler()
        parser = make_parser()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet

        parser.setFeature(handler.feature_external_ges, 0)

        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(xml_string))
        try:
            parser.parse(inpsrc)
            return chandler
        except:
            return None

    def parseHeader(self, file):
        # Create a parser
        parser = make_parser()
        chandler = theme_handler()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet
        try:
            parser.setFeature(handler.feature_external_ges, 0)
        except:
            pass
        inputsrc = InputSource()

        try:
            if type(file) is StringType:
                inputsrc.setByteStream(StringIO(file))
            else:
                filecontent = file.read()
                inputsrc.setByteStream(StringIO(filecontent))

            parser.parse(inputsrc)
            return chandler
        except:
            return None