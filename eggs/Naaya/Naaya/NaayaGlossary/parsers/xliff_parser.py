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


from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO
from types import StringType

#constants
_FILE_ATTRS = ['original', 'source-language', 'datatype', 'date',
          'target-language', 'product-name', 'product-version', 'build-num']
_PHASE_ATTRS = ['phase-name', 'process-name', 'tool', 'date', 'contact-name',
          'contact-email', 'company-name']


class xliff_handler(ContentHandler):
    """ This is used to parse the xliff file
    """

    def __init__(self):
        """constructor """
        self.__currentTag = ''
        self.__filetag = []
        self.__phase_group = []
        self.__source = 0
        self.__body = {}
        self.__data = []
        self.__inside_alttrans = 0
        self.__tuid = ''
        self.__approved = 1

    #functions related with <file> tag
    def getFileTag(self):
        return self.__filetag

    def setFileTag(self, dict):
        self.__filetag.extend(dict)

    #functions related with <phase-group> tag
    def getPhaseGroup(self):
        return self.__phase_group

    def getTuid(self):
        return self.__tuid

    def setPhaseGroup(self, dict):
        self.__phase_group.append(dict)

    def getBody(self):
        return self.__body

    def setBody(self, key, value):
        self.__body[key] = value

    def startElement(self, name, attrs):
        self.__currentTag = name

        if name == 'alt-trans':
            self.__inside_alttrans = 1
        # Make the attributes available
        # Implicit assumption: There is only one <file> element.
        if name == 'file':
            tmp = attrs.items()
            for i in [elem for elem in attrs.keys() if elem not in _FILE_ATTRS]:
                tmp.remove((i, attrs[i]))
            self.setFileTag(tmp)

        if name == 'phase':
            tmp = attrs.items()
            for i in [elem for elem in attrs.keys() if elem not in _PHASE_ATTRS]:
                tmp.remove((i, attrs[i]))
            self.setPhaseGroup(tmp)

        if name == 'trans-unit':
            self.__tuid = attrs['id']
            self.__approved = attrs['approved']
            self.__source = u''
            self.__target = u''
            self.__context = u''
            self.__context_name = u''
            self.__note = u''

        if name == 'context-group':
            self.__context_name = attrs['name']

    def endElement(self, name):
        if name == 'alt-trans':
            self.__inside_alttrans = 0

        if name == 'source' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__source = content

        if name == 'target' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__target = content

        if name == 'context-group' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__context = content

        if name == 'note' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__note = content

        if name == 'trans-unit':
            self.setBody((self.__tuid, self.__context_name), {'source':self.__source,
                                                              'target':self.__target,
                                                              'context':self.__context,
                                                              'context-name':self.__context_name,
                                                              'note':self.__note,
                                                              'approved':self.__approved})

        self.__currentTag = ''

    def characters(self, content):
        currentTag = self.__currentTag
        if currentTag in ( 'source', 'target', 'context-group', 'note'):
            self.__data.append(content)

class xliff_parser:
    """ class for parse xliff files """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        """ """
        chandler = xliff_handler()
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
        chandler = xliff_handler()
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