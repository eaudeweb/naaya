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
# Ghica Alexandru, Finsiel Romania

# python import
from xml.sax.handler import ContentHandler
from xml.sax import *
from types import StringType
from cStringIO import StringIO

# product imports
from Products.NaayaGlossary.utils import utils

class HandleTMXParsing(handler.ContentHandler, utils):
    """ Parse a TMX file"""
    def __init__(self):
        self.TMXContent = {}
        self.element = []
        self.element_id = ''
        self.translations = {}
        self.language = []
        self.__data = u''
        self.elements = {
         ('header'): (self.start_header,self.end_header),
         ('tu'): (self.start_tu,self.end_tu),
         ('tuv'): (self.start_tuv,self.end_tuv),
         ('seg'): (self.start_seg,self.end_seg),
         ('note'): (self.start_note,self.end_note),
          }

    def startElement(self, tag, attrs):
        """ This is the method called by SAX. We simply look
            up the tag in a list and then call the coresponding method
        """
        method = self.elements.get(tag, (None, None))[0]
        if method:
            method(tag,attrs)

    def endElement(self, tag):
        """ This is the method called by SAX. We simply look
            up the tag in a list and then call the coresponding method
        """
        method = self.elements.get(tag, (None, None))[1]
        if method:
            method(tag)

    def characters(self, text):
        """ This is the method called by SAX.
        """
        self.__data += text

    def start_header(self, tag, attrs):
        """ Start of header info """
        pass

    def end_header(self,tag):
        """ End of header info """
        pass

    def start_tu(self, tag, attrs):
        """ Translation unit """
        self.element = []
        self.translations = {}
        self.element_id = ''

    def end_tu(self,tag):
        """ Translation unit """
        self.element.append(self.element_id)
        self.element.append(self.translations)
        self.TMXContent[self.element[0]] = self.element[1]

    def start_tuv(self, tag, attrs):
        """ Translation Unit Variant """
        self.language = []
        if attrs.has_key("xml:lang"):
           self.language.append(attrs["xml:lang"])

    def end_tuv(self,tag):
        """ Translation Unit Variant """
        self.translations[self.language[0]] = self.language[1]

    def start_seg(self, tag, attrs):
        """ Start of segment """
        self.__data = u''

    def end_seg(self,tag):
        """ End of segment """
        self.language.append(self.__data)
        if self.language[0] == 'English' and self.language[1] != '':
            elem_name = self.utf8_to_latin1(self.language[1])
            self.element_id = self.ut_makeId(elem_name)

    def start_note(self, tag, attrs):
        """ Start of segment """
        pass

    def end_note(self,tag):
        """ End of segment """
        pass

class tmx_parser:
    def __init__(self):
        """ """
        pass
        
    def parseContent(self, file):
        # Create a parser
        parser = make_parser()
        chandler = HandleTMXParsing()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet
        try:
            parser.setFeature(handler.feature_external_ges, 0)
        except:
            pass
        inputsrc = InputSource()

        if type(file) is StringType:
            inputsrc.setByteStream(StringIO(file))
        else:
            filecontent = file.read()
            inputsrc.setByteStream(StringIO(filecontent))
        parser.parse(inputsrc)
        return chandler
        
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