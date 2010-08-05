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
      Reproduces a GML object structure and defines getters/setters for the elements
"""

from utils import utf8Encode

class GMLStructure:
    """ Reproduces a GML object structure and defines getters/setters for the elements """

    def __init__(self):
        """ constructor """
        #general
        self.__geo_name__=''
        #shp data
        self.__Fid__ = ''
        self.__rec_number__ = 0
        self.__feat_type__ = 0
        self.__xy_min__ = ()
        self.__xy_max__ = ()
        self.__rec_parts__ = []
        self.__rec_vertices__ = ()
        self.__shp_records__ = []
        #dbf data
        self.__rec_type__ = ''
        self.__rec_name__ = ''
        self.__rec_leng__ = ''
        self.__rec_decc__ = ''
        self.__rec_field__ = ()
        self.__records__ = []
        self.__dat_tag_name__ = ''
        self.__dat_tag_value__ = ''
        self.__dat_field__ = ()
        self.__dat_records__ = []
        self.__dbf_records__ = []

    ##################################################
    # Generic getters/setters
    ##################################################

    def getGeo_name(self):
        return (self.__geo_name__)

    def setGeo_name(self,geo_name):
        self.__geo_name__ = utf8Encode(geo_name)

    ##################################################
    # SHP data getters/setters
    ##################################################

    def getShp_records(self):
        return (self.__shp_records__)

    def setShp_records(self):
        self.__shp_records__.append (self.getRec_parts())

    def getFid(self):
        return (self.__Fid__)

    def setFid(self, Fid):
        self.__Fid__ = utf8Encode(Fid)

    def getRec_number(self):
        return (self.__rec_number__)

    def setRec_number(self,rec_number):
        self.__rec_number__ = utf8Encode(rec_number)

    def getFeat_type(self):
        return (self.__feat_type__)

    def setFeat_type(self, feat_type):
        self.__feat_type__ = utf8Encode(feat_type)

    def getXY_min(self):
        return (self.__xy_min__)

    def setXY_min(self,x_min,y_min):
        self.__xy_min__ = utf8Encode(x_min),utf8Encode(y_min)

    def getXY_max(self):
        return (self.__xy_max__)

    def setXY_max(self,x_max,y_max):
        self.__xy_max__ = utf8Encode(x_max),utf8Encode(y_max)

    def getRec_parts(self):
        return (self.__rec_parts__)

    def setRec_parts(self,rec_parts):
        self.__rec_parts__.append(rec_parts)

    def resetRec_parts(self):
        self.__rec_parts__ = []

    def getRec_vertices(self):
        return (self.__rec_vertices__)

    def setRec_vertices(self,vertices):
        self.__rec_vertices__ = vertices

    def resetRec_vertices(self):
        self.__rec_vertices__ = ()

    ##################################################
    # DBF data getters/setters
    ##################################################

    def getDat_tag_name(self):
        return (self.__dat_tag_name__)

    def setDat_tag_name(self,dat_tag_name):
        self.__dat_tag_name__ = utf8Encode(dat_tag_name)

    def getDat_tag_value(self):
        return (self.__dat_tag_value__)

    def setDat_tag_value(self,dat_tag_value):
        self.__dat_tag_value__ = utf8Encode(dat_tag_value)

    def getDat_field(self):
        return (self.__dat_field__)

    def setDat_field(self):
        self.__dat_field__ = (self.getDat_tag_name(), self.getDat_tag_value())

    def getDat_records(self):
        return (self.__dat_records__)

    def setDat_records(self):
        self.__dat_records__.append (self.getDat_field())

    def resetDat_records(self):
        self.__dat_records__ = []

    def getDbf_records(self):
        return (self.__dbf_records__)

    def setDbf_records(self):
        self.__dbf_records__.append (self.getDat_records())

    def getRec_field(self):
        return (self.__rec_field__)

    def setRec_field(self):
        self.__rec_field__ = (self.getRec_type(), self.getRec_name(), self.getRec_leng(), self.getRec_decc())

    def getRec_dbf(self):
        return (self.__records__)

    def setRec_dbf(self):
        self.__records__.append (self.getRec_field())

    def getRec_type(self):
        return (self.__rec_type__)

    def setRec_type(self,rec_type):
        self.__rec_type__ = utf8Encode(rec_type)

    def getRec_name(self):
        return (self.__rec_name__)

    def setRec_name(self,rec_name):
        self.__rec_name__ = utf8Encode(rec_name)

    def getRec_leng(self):
        return (self.__rec_leng__)

    def setRec_leng(self,rec_leng):
        self.__rec_leng__ = utf8Encode(rec_leng)

    def getRec_decc(self):
        return (self.__rec_decc__)

    def setRec_decc(self,rec_decc):
        self.__rec_decc__ = utf8Encode(rec_decc)