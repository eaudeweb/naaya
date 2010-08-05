#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "EWGeoMap"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania and Eau de Web 
#are Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#        Bogdan Grama (Finsiel Romania)
#        Iulian Iuga (Finsiel Romania)
#  Porting to Naaya: 
#        Cornel Nitu (Eau de Web)


__doc__ = """
    GML schema definition parser module.
"""

from gml                import GMLStructure
from xml.sax.handler    import ContentHandler
from xml.sax            import *
from cStringIO          import StringIO
from types              import StringType

_DATA_TAGS = ['xs:element']

def gml_sd_import(file):
    """ gml_sd_import class """

    gml_sd_val = GMLStructure()
    parser = gml_sd_parser()

    #parse the gml_sd information
    chandler = parser.parseHeader(file, gml_sd_val)
    try:
        gml_obj = chandler.getGmlSdVal()
    except Exception:
        raise Exception, 'GML schema is not valid'

    #return an GMLStructure object with dbf structure information 
    return gml_obj


class gml_sd_handler(ContentHandler):
    """ This is used to parse the gml_sd files """

    def __init__(self, gml_sd_val):
        """ constructor """
        self.gml_sd_val = gml_sd_val
        self.__currentTag = ''
        self.__data = []
        self.l_coord_marker = 0
        self.__tagout=''

    def getdbfdata(self):
        return self.__dbfdata

    def getGmlSdVal(self):
        return self.gml_sd_val

    def startElement(self, name, attrs):
        if name == 'xs:element':
            for elem in attrs.keys():
                if elem == 'name':
                    self.gml_sd_val.setRec_name(attrs['name']) 
        if name == 'xs:restriction':
            for elem in attrs.keys():
                if elem == 'base':
                    #clean 'xs:'
                    type_tmp = attrs['base']
                    type_tmp = type_tmp[-(len(type_tmp)-len('xs:')):]
                    self.gml_sd_val.setRec_type(type_tmp)

        if name == 'xs:maxLength':
            for elem in attrs.keys():
                if elem == 'value':
                    self.gml_sd_val.setRec_leng(attrs['value']) 
                    if self.gml_sd_val.getRec_type() == 'string':
                        self.__tagout = 1

        if name == 'xs:totalDigits':
            for elem in attrs.keys():
                if elem == 'value':
                    self.gml_sd_val.setRec_leng(attrs['value'])
                    if self.gml_sd_val.getRec_type() == 'integer':
                        self.__tagout = 1

        if name == 'xs:fractionDigits':
            for elem in attrs.keys():
                if elem == 'value':
                    self.gml_sd_val.setRec_decc(attrs['value'])
                    self.__tagout = 1

        if self.__tagout == 1:
            if self.gml_sd_val.getRec_decc() == '':
               self.gml_sd_val.setRec_decc('0') 
            self.gml_sd_val.setRec_field()
            self.gml_sd_val.setRec_type('') 
            self.gml_sd_val.setRec_name('')
            self.gml_sd_val.setRec_leng('')
            self.gml_sd_val.setRec_decc('')
            self.gml_sd_val.setRec_dbf()
            self.__tagout=0            

        self.__currentTag = name

    def endElement(self, name):
        if name == 'xs:restriction':
            if self.gml_sd_val.getRec_type() == 'string':
                self.__tagout = 1
        if self.__tagout == 1:
            if self.gml_sd_val.getRec_decc() == '':
               self.gml_sd_val.setRec_decc('0') 
            self.gml_sd_val.setRec_field()
            self.gml_sd_val.setRec_type('') 
            self.gml_sd_val.setRec_name('')
            self.gml_sd_val.setRec_leng('')
            self.gml_sd_val.setRec_decc('')
            self.gml_sd_val.setRec_dbf()
            self.__tagout=0

        self.__currentTag = ''

    def characters(self, content):
        currentTag = self.__currentTag
        if currentTag in _DATA_TAGS:
            self.__data.append(content)

class gml_sd_parser:
    """ Class for parse gml_sd files """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        # Parse content
        parser = make_parser()
        chandler = gml_sd_handler()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)

        parser.setFeature(handler.feature_external_ges, 0)

        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(xml_string))
        try:
            parser.parse(inpsrc)
            return chandler
        except:
            return None

    def parseHeader(self, file, gml_sd_val):
        # Create a parser
        parser = make_parser()
        chandler = gml_sd_handler(gml_sd_val)
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)

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