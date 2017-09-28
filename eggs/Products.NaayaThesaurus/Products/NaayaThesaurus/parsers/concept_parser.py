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

class concept_handler(ContentHandler):
    """ This is used to parse the relation file """

    def __init__(self):
        """ constructor """
        self.__concepts = {}
        self.__themes = {}
        self.__concept_id = ''
        self.__theme_id = ''

    def getConcepts(self):
        return self.__concepts

    def setConcepts(self, key, value):
        self.__concepts[key] = value

    def getThemes(self):
        return self.__themes

    def setThemes(self, key, value):
        self.__themes[key] = value

    def startElement(self, name, attrs):
        if name == 'rdf:Description':
            self.__concept_id = attrs['rdf:about']

        if name == 'thesaurus:theme':
            self.__theme_id = attrs['rdf:resource']
            self.setThemes((self.__concept_id, self.__theme_id),
                           {'concept_id':self.__concept_id,
                            'theme_id':self.__theme_id})

    def endElement(self, name):
        if name == 'rdf:Description':
            self.setConcepts(self.__concept_id,
                            {'concept_id':self.__concept_id})

class concept_parser:
    """ class for parse relation files """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        """ """
        chandler = concept_handler()
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
        chandler = concept_handler()
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