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


from xml.sax.handler                    import ContentHandler
from xml.sax                            import *
from cStringIO                          import StringIO
from types                              import StringType

from Products.NaayaThesaurus.utils      import th_utils

#constants
_RDF_ATTRS = ['xml:lang']
_DATA_TAGS = ['skos:prefLabel', 'skos:altLabel', 'rdf:source', 'skos:definition', 'skos:scopeNote', 'thesaurus:def_src']


class term_handler(ContentHandler):
    """ This is used to parse the term file
    """

    def __init__(self):
        """ constructor """
        self.__currentTag = ''
        self.__data = []
        self.__pref = {}
        self.__alt = {}
        self.__def = {}
        self.__src = {}
        self.__def_src = {}
        self.__scope = {}
        self.__langcode = ''
        self.__concept_id = ''
        self.__source_id = ''

    def getLanguage(self):
        return self.__langcode

    def getPref(self):
        return self.__pref

    def setPref(self, key, value):
        self.__pref[key] = value

    def getAlt(self):
        return self.__alt

    def setAlt(self, key, value):
        self.__alt[key] = value

    def getDef(self):
        return self.__def

    def setDef(self, key, value):
        self.__def[key] = value

    def getScope(self):
        return self.__scope

    def setScope(self, key, value):
        self.__scope[key] = value

    def getSrc(self):
        return self.__src

    def setSrc(self, key, value):
        self.__src[key] = value

    def getDefSrc(self):
        return self.__def_src

    def setDefSrc(self, key, value):
        self.__def_src[key] = value

    def startElement(self, name, attrs):
        self.__currentTag = name

        if name == 'rdf:RDF':
            for elem in attrs.keys():
                elem = elem.encode('utf-8')
                if elem in _RDF_ATTRS:
                    self.__langcode = attrs['xml:lang']

        if name == 'skos:Concept':
            self.__concept_id = attrs['rdf:about']

    def endElement(self, name):
        if name == 'skos:prefLabel':
            content = u''.join(self.__data).strip()
            self.__data = []
            self.setPref(self.__concept_id,
                         {'concept_id':self.__concept_id,
                          'concept_name':content})

        if name == 'skos:altLabel':
            content = u''.join(self.__data).strip()
            self.__data = []
            self.setAlt(self.__concept_id,
                        {'concept_id':self.__concept_id,
                         'alt_name':content})

        if name == 'skos:definition':
            content = u''.join(self.__data).strip()
            self.__data = []
            self.setDef(self.__concept_id,
                        {'concept_id':self.__concept_id,
                         'definition':content})

        if name == 'skos:scopeNote':
            content = u''.join(self.__data).strip()
            self.__data = []
            self.setScope(self.__concept_id,
                         {'concept_id':self.__concept_id,
                          'scope_note':content})

        if name == 'rdf:source':
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__source_id = th_utils().utGenRandomId()
            self.setSrc(self.__source_id,
                        {'source_id':self.__source_id,
                         'source_name':content,
                         'concept_id':self.__concept_id})

        if name == 'thesaurus:def_src':
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__source_id = th_utils().utGenRandomId()
            self.setDefSrc((self.__concept_id, self.__source_id),
                           {'source_id':self.__source_id,
                            'source_name':content,
                            'concept_id':self.__concept_id})

        self.__currentTag = ''

    def characters(self, content):
        currentTag = self.__currentTag
        if currentTag in _DATA_TAGS:
            self.__data.append(content)

class term_parser:
    """ class for parse term files """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        """ """
        chandler = term_handler()
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
        chandler = term_handler()
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