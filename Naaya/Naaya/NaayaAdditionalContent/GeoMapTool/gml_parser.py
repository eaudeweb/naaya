# -*- coding: latin1 -*-
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
    GML parser module
"""

from xml.sax.handler import ContentHandler
from xml.sax         import *
from cStringIO       import StringIO
from types           import StringType

_DATA_TAGS = ['gml:X', 'gml:Y', 'gml:coordinates']
_DATA_SD_TAGS = []
_DATA_ID = ''

def gml_import(file, struct_gml):
    """ """
    #fill special tag name
    _DATA_ID = 'reportnet'

    #fill data tags from schema    
    dt_ap = _DATA_SD_TAGS.append
    for i in range(len(struct_gml.getRec_dbf())):
        ttype, tname, tlen, tdecc = (struct_gml.getRec_dbf())[i]
        dt_ap ('%s' % tname)

    #parse the GML information
    parser = gml_parser()
    chandler = parser.parseHeader(file,struct_gml)
    chandler.setBoundBox()

    ret_struct_gml = chandler.getGMLData()

    return ret_struct_gml

class gml_handler(ContentHandler):
    """ This is used to parse the GML files
    """

    def __init__(self, struct_gml):
        """ constructor """
        # struct_gml
        self.struct_gml = struct_gml
        
        self.__currentTag = ''
        self.__data = []
        self.__data_sd = []
        self.e_fID = ''
        self.x_min = ''
        self.y_min = ''
        self.x_max = ''
        self.y_max = ''
        self.l_coord_marker = 0
        self.l_polygon_marker = 0
        self.l_line_marker = 0

    def getGMLData(self):
        return self.struct_gml        

    def setBoundBox(self):
        self.struct_gml.setXY_min (self.x_min, self.y_min)
        self.struct_gml.setXY_max (self.x_max, self.y_max)

    def startElement(self, name, attrs):
        if name == _DATA_ID:
            for elem in attrs.keys():
                if elem == 'fid':
                    self.struct_gml.setFid(attrs['fid'])

        if name == 'gml:Polygon':
            self.l_polygon_marker = 1 

        if name == 'gml:LineString':
            self.l_line_marker = 1

        self.__currentTag = name
       
    def endElement(self, name):
        #START bounding box
        if name == 'gml:X':
            if self.l_coord_marker:
                self.x_max = u''.join(self.__data).strip()
            else:
                self.x_min = u''.join(self.__data).strip()
            self.__data = []
                
        if name == 'gml:Y':
            if self.l_coord_marker:
                self.y_max = u''.join(self.__data).strip()
            else:
                self.y_min = u''.join(self.__data).strip()
            self.__data = []
        #END bounding box  
        
        #START geometry
        if name == 'gml:coordinates':
            tup_final = []
            listver = (u''.join(self.__data).strip()).split(' ')
            for ver in listver:
                tup = ver.split(',')
                tupa = tup[0]
                tupb = tup[1]
                tup_final.append ((float(tupa),float(tupb)))
            self.struct_gml.setRec_parts(tup_final)
            #clean
            self.struct_gml.resetRec_vertices()
            self.__data = []    

        if name == 'gml:Point':
            self.struct_gml.setFeat_type('1')
            self.struct_gml.setShp_records()
            self.struct_gml.resetRec_parts()

        if name == 'gml:LineString':
            self.struct_gml.setFeat_type('3')

        if name == 'gml:Polygon':
            self.struct_gml.setFeat_type('5') 

        if name == 'gml:featureMember':
            if self.struct_gml.getFeat_type() == '5':
                if self.l_polygon_marker:
                    self.struct_gml.setShp_records()
                    self.struct_gml.resetRec_parts()
            if self.struct_gml.getFeat_type() == '3':
                if self.l_line_marker:
                    self.struct_gml.setShp_records()
                    self.struct_gml.resetRec_parts()
            
        if name == 'gml:coord':
            self.l_coord_marker = 1
        #END geometry
        #Start DBF data tags    
        if name in _DATA_SD_TAGS:
            self.struct_gml.setDat_tag_name(name)
            self.struct_gml.setDat_tag_value(u''.join(self.__data_sd).strip())
            #fill list
            self.struct_gml.setDat_field()
            #clean
            self.struct_gml.setDat_tag_name('')
            self.struct_gml.setDat_tag_value('')
            self.struct_gml.setDat_records()
            self.__data_sd = []

        if name == 'gml:featureMember':
            self.struct_gml.setDbf_records()
            self.struct_gml.resetDat_records()

        self.__currentTag = ''
        #END DBF data tags 

    def characters(self, content):
        currentTag = self.__currentTag
        if currentTag in _DATA_TAGS:
            self.__data.append(content)
        if currentTag in _DATA_SD_TAGS:
            self.__data_sd.append(content)


class gml_parser:
    """ class for parse GML files """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        """ """
        parser = make_parser()
        chandler = gml_handler()

        parser.setContentHandler(chandler)
        parser.setFeature(handler.feature_external_ges, 0)

        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(xml_string))
        try:
            parser.parse(inpsrc)
            return chandler
        except:
            return None

    def parseHeader(self, file, struct_gml):
        # Create a parser
        parser = make_parser()
        chandler = gml_handler(struct_gml)
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        try:
            parser.setFeature(handler.feature_external_ges, 0)
        except:
            pass
        inputsrc = InputSource()
        
        if type(file) is StringType:
            inputsrc.setByteStream(StringIO(file))
        else:
            filecontent = file.readline()
            inputsrc.setByteStream(StringIO(filecontent))
        parser.parse(inputsrc)
        return chandler
        
        try:
            if type(file) is StringType:
                inputsrc.setByteStream(StringIO(file))
            else:
                filecontent = file.readline()
                inputsrc.setByteStream(StringIO(filecontent))
            parser.parse(inputsrc)
            return chandler
        except:
            return None    