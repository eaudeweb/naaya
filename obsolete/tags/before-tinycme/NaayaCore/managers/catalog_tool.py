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
# Cornel Nitu, Eau de Web
# Dragos Chirila, Finsiel Romania
# Miruna Badescu, Eau de Web
#
#$Id: catalog_tool.py 3641 2005-05-17 09:16:10Z chiridra $

#Python imports

#Zope imports
from AccessControl import getSecurityManager
from AccessControl.Permissions import view

#Product imports
class catalog_tool:
    """ This class is responsable with API for ZCatalog object """

    def __init__(self):
        """ """
        pass

    def __buildCatalogPath(self, p_item):
        """Creates an id for the item to be added in catalog"""
        return '/'.join(p_item.getPhysicalPath())

    def __searchCatalog(self, p_criteria):
        """Search catalog"""
        return self.getCatalogTool()(p_criteria)

    def __getObjects(self, p_brains):
        """ """
        try:
            #return map(lambda x: x.getObject(), p_brains)
            return map(self.portal_catalog.getobject, map(getattr, p_brains, ('data_record_id_',)*len(p_brains)))
        except:
            return []

    def __getObjectsAndScore(self, p_brains):
        """ """
        try:
            return map(lambda x: (x.getObject(), x.data_record_score_), p_brains)
        except:
            return []

    def __eliminateDuplicates(self, p_objects):
        """Eliminate duplicates from a list of objects (with ids)"""
        dict = {}
        for l_object in p_objects:
            dict[l_object.id] = l_object
        return dict.values()

    #################################
    #      INTERFACE METHODS        #
    #################################
    def catalogNyObject(self, p_ob):
        try: self.getCatalogTool().catalog_object(p_ob, self.__buildCatalogPath(p_ob))
        except: pass

    def uncatalogNyObject(self, p_ob):
        try: self.getCatalogTool().uncatalog_object(self.__buildCatalogPath(p_ob))
        except: pass

    def recatalogNyObject(self, p_ob):
        try:
            catalog_tool = self.getCatalogTool()
            l_ob_path = self.__buildCatalogPath(p_ob)
            catalog_tool.uncatalog_object(l_ob_path)
            catalog_tool.catalog_object(p_ob, l_ob_path)
        except:
            pass

    def findCatalogedObjects(self, p_query, p_path, lang):
        l_result = []
        l_filter = {'submitted': 1, 'approved': 1} #only submitted items
        l_filter['meta_type'] = self.searchable_content #only the specified meta types
        l_filter['path'] = p_path
        #search in 'keywords'
        l_criteria = l_filter.copy()
        l_criteria['objectkeywords_%s' % lang] = p_query
        l_result.extend(self.__searchCatalog(l_criteria))
        l_criteria = l_filter.copy()
        l_criteria['PrincipiaSearchSource'] = p_query
        l_result.extend(self.__searchCatalog(l_criteria))
        return l_result

    def searchCatalog(self, p_query, p_path, lang):
        """ """
        if type(p_query) == type(''):
            l_results = self.__getObjects(self.__eliminateDuplicates(self.findCatalogedObjects(p_query, p_path, lang)))
        else:
            l_results = self.__getObjects(self.__eliminateDuplicates(self.findCatalogedObjectsByGenericQuery(p_query)))
        return l_results

    def findCatalogedObjectsByGenericQuery(self, p_query):
        return self.__searchCatalog(p_query)

    def clearCatalog(self):
        self.__clearCatalog()
        self._p_changed = 1

    def getCatalogedObjects(self, meta_type=None, approved=0, howmany=-1, sort_on='releasedate', sort_order='reverse', has_local_role=0, **kwargs):
        l_results = []
        l_filter = {'submitted': 1} #only submitted items
        if approved == 1: l_filter['approved'] = 1
        if has_local_role == 1: l_filter['has_local_role'] = 1
        if sort_on != '':
            l_filter['sort_on'] = sort_on
            if sort_order != '':
                l_filter['sort_order'] = sort_order
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        #extra filters
        l_filter.update(kwargs)
        #perform the search
        l_results = self.__searchCatalog(l_filter)
        if howmany != -1:
            l_results = l_results[:howmany]
        l_results = self.__getObjects(l_results)
        return l_results

    # The function getCatalogedObjects did not allow searching for not-approved objects
    # It needs to be replaced with the one below once we'll make sure it doesn't change any behavior
    def getCatalogedObjectsA(self, meta_type=None, approved=None, howmany=-1, sort_on='releasedate', sort_order='reverse', has_local_role=0, **kwargs):
        l_results = []
        l_filter = {'submitted': 1} #only submitted items
        if approved == 1:
            l_filter['approved'] = 1
        elif approved == 0:
            l_filter['approved'] = 0
        if has_local_role == 1: l_filter['has_local_role'] = 1
        if sort_on != '':
            l_filter['sort_on'] = sort_on
            if sort_order != '':
                l_filter['sort_order'] = sort_order
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        #extra filters
        l_filter.update(kwargs)
        #perform the search
        l_results = self.__searchCatalog(l_filter)
        if howmany != -1:
            l_results = l_results[:howmany]
        l_results = self.__getObjects(l_results)
        return l_results

    # This function is similar to getCatalogedObjects, but also checks for view permission on objects
    def getCatalogedObjectsCheckView(self, meta_type=None, approved=0, howmany=-1, sort_on='releasedate', sort_order='reverse', has_local_role=0, **kwargs):
        l_results = []
        l_filter = {'submitted': 1} #only submitted items
        if approved == 1: l_filter['approved'] = 1
        if has_local_role == 1: l_filter['has_local_role'] = 1
        if sort_on != '':
            l_filter['sort_on'] = sort_on
            if sort_order != '':
                l_filter['sort_order'] = sort_order
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        #extra filters
        l_filter.update(kwargs)
        #perform the search
        l_results = self.__searchCatalog(l_filter)
        if howmany == -1:
            l_objects = self.__getObjects(l_results)
            return [obj for obj in l_objects if getSecurityManager().checkPermission(view, obj)]
        else:
            if howmany > len(l_results):
                howmany = len(l_results)
            l_temp = l_results[:howmany]
            l_all = len(l_results)
            l_objects = self.__getObjects(l_temp)
            l_output = []
            l_counter = howmany
            while len(l_temp) > 0:
                l_output.extend([obj for obj in l_objects if getSecurityManager().checkPermission(view, obj)])
                if len(l_output) >= howmany:
                    return l_output[:howmany]
                else:
                    l_temp = l_results[l_counter:l_counter+howmany]
                    l_counter = l_counter + howmany
                    l_objects = self.__getObjects(l_temp)

    def getCatalogedUnsubmittedObjects(self, meta_type=None):
        """
        Returns a list with all I{brain} objects that are not submitted.
        """
        l_filter = {'submitted': 0}
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        return self.__getObjects(self.__searchCatalog(l_filter))

    def getCatalogedBrains(self, meta_type=None):
        """
        Returns a list with all I{brain} objects in the catalog.
        """
        l_filter = {}
        if meta_type is not None: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        return self.__searchCatalog(l_filter)

    def query_objects_ex(self, meta_type=None, q=None, lang=None, path=None, howmany=-1, **kwargs):
        l_results = []
        l_filter = {'submitted': 1} #only submitted items
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        if path is not None: l_filter['path'] = path
        for key, value in kwargs.items():
            if value is not None: l_filter[key] = value
        if q is not None:
            if lang is not None:
                l_filter['objectkeywords_%s' % lang] = q
                l_results.extend(self.__searchCatalog(l_filter))
                l_filter.pop('objectkeywords_%s' % lang)
            l_filter['PrincipiaSearchSource'] = q
        l_results.extend(self.__searchCatalog(l_filter))
        if howmany != -1: l_results = l_results[:howmany]
        return self.__getObjects(l_results)

    def query_translated_objects(self, meta_type=None, lang=None, approved=0, howmany=-1, sort_on='releasedate', sort_order='reverse', **kwargs):
        l_results = []
        l_filter = {'submitted': 1} #only submitted items
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        if lang is not None: l_filter['istranslated_%s' % lang] = 1
        if approved == 1: l_filter['approved'] = 1
        if sort_on != '':
            l_filter['sort_on'] = sort_on
            if sort_order != '': l_filter['sort_order'] = sort_order
        for key, value in kwargs.items():
            if value is not None: l_filter[key] = value
        l_results = self.__searchCatalog(l_filter)
        if howmany != -1: l_results = l_results[:howmany]
        return self.__getObjects(l_results)

    def getCommentedObjects(self):
        return self.__getObjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'has_comments': 1}))

    def getCatalogCheckedOutObjects(self):
        return self.__getObjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'checkout': 1}))

    def getNotCheckedObjects(self):
        return self.__getObjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'validation_status': 0}))

    def getCheckedOkObjects(self):
        return self.__getObjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'validation_status': 1}))

    def getCheckedNotOkObjects(self):
        return self.__getObjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'validation_status': -1}))
