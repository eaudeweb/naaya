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


#Python imports
import string
import codecs
import re
from copy import deepcopy

#Zope imports
from Products.PythonScripts.standard import url_quote

#product imports
from constants import *

#constants
class utils:

    def __init__(self):
        self.win_cp1252 = {
                128: 8364, # euro sign
                130: 8218, # single low-9 quotation mark
                131:  402, # latin small letter f with hook
                132: 8222, # double low-9 quotation mark
                133: 8230, # horizontal ellipsis
                134: 8224, # dagger
                135: 8225, # double dagger
                136:  710, # modifier letter circumflex accent
                137: 8240, # per mille sign
                138:  352, # latin capital letter s with caron
                139: 8249, # single left-pointing angle quotation mark
                140:  338, # latin capital ligature oe
                142:  381, # latin capital letter z with caron
                145: 8216, # left single quotation mark
                146: 8217, # right single quotation mark
                147: 8220, # left double quotation mark
                148: 8221, # right double quotation mark
                149: 8226, # bullet
                150: 8211, # en dash
                151: 8212, # em dash
                152:  732, # small tilde
                153: 8482, # trade mark sign
                154:  353, # latin small letter s with caron
                155: 8250, # single right-pointing angle quotation mark
                156:  339, # latin small ligature oe
                158:  382, # latin small letter z with caron
                159:  376} # latin capital letter y with diaeresis

    def ut_test_even(self, p_number):
        """ return true if even """
        return not(p_number%2)

    def ut_test_definition(self, p_def):
        """."""
        if p_def == 'Definition':
            return 1
        return 0

    def ut_makeId(self, p_name):
        """ generate the ID """
        transtab=string.maketrans('/ +@','____')
        p_name = unicode(p_name, 'latin-1')
        p_name = string.lower(p_name.encode('ascii', 'replace'))
        return string.translate(p_name,transtab,'?&!;()<=>*#[]{}^~:|\/???$?%?')

    def element_list_sorted(self):
        """ return all elements from a Centre root """
        lista=self.objectItems([NAAYAGLOSSARY_ELEMENT_METATYPE])
        lista.sort()
        return lista

    def utGetElement(self,p_name):
        """ return an element from catalog """
        cat_obj = self.cu_get_cataloged_objects(meta_type=NAAYAGLOSSARY_ELEMENT_METATYPE)
        for obj in cat_obj:
            if obj.name == p_name:
                return obj

    def utAddObjectAction(self, REQUEST=None):
        """ check if adding an object """
        res = 0
        if REQUEST:
            res = REQUEST.has_key('add')
        return res

    def utUpdateObjectAction(self, REQUEST=None):
        """ check if updating an object """
        res = 0
        if REQUEST:
            res = REQUEST.has_key('update')
        return res

    def utDeleteObjectAction(self, REQUEST=None):
        """ check if deleting an object """
        res = 0
        if REQUEST:
            res = REQUEST.has_key('delete')
        return res

    def utConvertToList(self, something):
        """ convert to list """
        ret = something
        if type(something) is type(''):
            ret = [something]
        return ret

    def utConvertToInt(self, in_str):
        """ converts a string to an integer """
        out_num = 0
        if in_str[0] == "-":
            multiplier = -1
            in_str = in_str[1:]
        else:
            multiplier = 1
        for x in range(0,len(in_str)):
            out_num = out_num * 10 + ord(in_str[x]) - ord('0')
        return out_num * multiplier

    def utSortList(self, list):
        """ sort a list """
        list.sort()
        return list

    def utUrlEncode(self, p_string):
        """ encode a string using url_encode """
        return url_quote(p_string)

    def utISOFormat(self):
        """ return the currect time in ISO format """
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def utIsEmptyString(self, term='',REQUEST=None):
        """ return true if a string contains only white characters """
        if term and len(term)>0:
            if term.count(" ") == len(term):
                return 1
            return 0
        return 1

    def utGetObject(self, url):
        """ get an object given the url """
        return self.unrestrictedTraverse(url, None)

    def utSortListOfDictionariesByKey(self, p_list, p_key, p_order=0):
        """ sort a list of dictionary by key """
        if p_order==0:   #ascending
            p_list.sort(lambda x, y, param=p_key: cmp(x[param], y[param]))
        else:            #desceding
            p_list.sort(lambda x, y, param=p_key: cmp(y[param], x[param]))

    def utf8_to_latin1(self, s):
        return s.decode('utf-8').encode('latin-1')

    def debug(self, error):
        """ """
        import sys
        return str(error) + ' at line ' + str(sys.exc_info()[2].tb_lineno)

    def convertValToHex(self, val):
        return unichr(int(val.group()[2:-1]))

    def convertHTMLCodesToHex(self, term):
        import re
        return re.sub('&#[0-9]+;', self.convertValToHex, term)

    def convertWinCodesToHTMLCodes(self, term):
        for i in range(len(term)-1,-1,-1):
            if ord(term[i]) in self.win_cp1252.keys():
                term=term[0:i] + "&#" + str(self.win_cp1252[ord(term[i])]) + ";" + term[i+1:]
        return term

    def joinToList(self, l):
        """Gets a list and returns a comma separated string"""
        return string.join(l, ',')

    def addToList(self, l, v):
        """Return a new list, after adding value v"""
        res = deepcopy(l)
        try:
            res.append(v)
        except:
            pass
        return res

    def removeFromList(self, l, v):
        """Return a new list, after removing value v"""
        res = deepcopy(l)
        try:
            res.remove(v)
        except:
            pass
        return res

    def utIsElement(self):
        """ check if the object is a element """
        if self.parent_anchors:
            return True
        else:
            return self.meta_type==NAAYAGLOSSARY_ELEMENT_METATYPE

class catalog_utils:

    def __init__(self):
        """ """
        pass

    def __build_catalog_path(self, item):
        """ creates an id for the item to be added in catalog """
        return '/'.join(item.getPhysicalPath())

    def __searchCatalog(self, criteria):
        """ search catalog """
        catalog = self.getGlossaryCatalog()
        return catalog(criteria)

    def __get_objects(self, brains):
        """ given the brains return the objects """
        catalog = self.getGlossaryCatalog()
        try:
            return map(catalog.getobject, map(getattr, brains, ('data_record_id_',)*len(brains)))
        except:
            return []

    def cu_catalog_object(self, ob):
        """ catalog an object """
        catalog = self.getGlossaryCatalog()
        try:
            ob_path = self.__build_catalog_path(ob)
            catalog.catalog_object(ob, ob_path)
        except Exception, error:
            print self.debug(error)

    def cu_uncatalog_object(self, ob):
        """ uncatalog an object """
        catalog = self.getGlossaryCatalog()
        try:
            catalog.uncatalog_object(self.__build_catalog_path(ob))
        except Exception, error:
            print self.debug(error)

    def cu_recatalog_object(self, ob):
        """ recatalog an object """
        try:
            catalog = self.getGlossaryCatalog()
            ob_path = self.__build_catalog_path(ob)
            if catalog.getrid(ob_path) is not None:
                catalog.uncatalog_object(ob_path)
            self.cu_catalog_object(ob)
        except Exception, error:
            print self.debug(error)
            
    def cu_getIndexes(self):
        """ return a list with all ZCatalog indexes """
        catalog = self.getGlossaryCatalog()
        return catalog.index_objects()

    def cu_get_cataloged_objects(self, meta_type=None, approved=0, howmany=-1, sort_on='bobobase_modification_time', 
        sort_order='reverse', path=''):
        """ return objects from catalog """
        results = []
        filter = {}
        filter['path'] = path
        if approved == 1:
            filter['approved'] = 1
        if sort_on != '':
            filter['sort_on'] = sort_on
            if sort_order != '':
                filter['sort_order'] = sort_order
        if meta_type:
            filter['meta_type'] = self.utConvertToList(meta_type)

        results = self.__searchCatalog(filter)
        if howmany != -1:
            results = results[:howmany]
        results = self.__get_objects(results)
        return results

    def utEliminateDuplicates(self, p_objects):
        """Eliminate duplicates from a list of objects (with ids)"""
        dict = {}
        for l_object in p_objects:
            dict[l_object.id] = l_object
        return dict.values()

    def cu_get_codes_by_name(self, meta_type=None, name=None):
        """ retrieve objects codes given the name """
        catalog = self.getGlossaryCatalog()
        filter = {}
        if meta_type:
            filter['meta_type'] = self.utConvertToList(meta_type)
        if name:
            filter['name'] = self.utConvertToList(name)
        return self.__searchCatalog(filter)

    def cu_search_catalog(self, meta_type=None, query='', size=10000, language='English', definition=''):
        """ search catalog """
        catalog = self.getGlossaryCatalog()
        query = self.StrEscapeForSearch(query)
        command= "catalog(meta_type=meta_type, %s=query, definition=definition)" % self.cookCatalogIndex(language)
        results = eval(command)
        res = self.__get_objects(results)
        return self.utEliminateDuplicates(res)[:int(size)]

    def cu_search_catalog_by_id(self, id=''):
        """ search catalog """
        filter = {}
        filter['id'] = id
        filter['meta_type'] = NAAYAGLOSSARY_ELEMENT_METATYPE
        res = self.__searchCatalog(filter)
        return res

    def cu_get_folder_by_id(self, id=''):
        """ return folder object given the id """
        filter = {}
        if id:
            filter['id'] = id
            filter['meta_type'] = NAAYAGLOSSARY_FOLDER_METATYPE
            results = self.__searchCatalog(filter)
            return self.__get_objects(results)
        return []

    def StrEscapeForSearch(self, p_string):
        """ escape some characters"""
        return re.sub('[(\"{})\[\]]', '', p_string)

    def cookCatalogIndex(self, index_name):
        """ cook catalog index name """
        return index_name.replace('/', '_').replace('-', '_').replace(' ', '_')
