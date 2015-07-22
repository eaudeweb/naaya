
from AccessControl import getSecurityManager
from AccessControl.Permissions import view
from OFS.Uninstalled import BrokenClass

from naaya.core.zope2util import ofs_path

class catalog_tool(object):
    """
    This is a mixing class derived by NySite
    which is responsible with API for ZCatalog object

    """

    def __buildCatalogPath(self, p_item):
        """Creates an id for the item to be added in catalog"""
        return '/'.join(p_item.getPhysicalPath())

    def __searchCatalog(self, p_criteria):
        """Search catalog"""
        return self.getCatalogTool()(p_criteria)

    def __getObjectsAndScore(self, p_brains):
        """ """
        output = []
        for brain in p_brains:
            try:
                ob = brain.getObject()
                drs = brain.data_record_score_
            except:
                self.log_current_error()
            output.append( (ob, drs) )
        return output

    def __eliminateDuplicates(self, p_objects):
        """Eliminate duplicates from a list of objects (with ids)"""
        dict = {}
        for l_object in p_objects:
            dict[l_object.id] = l_object
        return dict.values()

    #################################
    #      INTERFACE METHODS        #
    #################################
    def safe_getobjects(self, p_brains):
        """ getobject on each brain in list and filter&log getobject errors """
        output = []
        for brain in p_brains:
            try:
                ob = self.portal_catalog.getobject(brain.data_record_id_)
                if isinstance(ob, BrokenClass):
                    raise ValueError("Broken object in catalog: %r" %
                                     brain.getPath())
            except:
                self.log_current_error()
            else:
                output.append(ob)
        return output

    def catalogNyObject(self, p_ob):
        try: self.getCatalogTool().catalog_object(p_ob, self.__buildCatalogPath(p_ob))
        except: self.log_current_error()

    def uncatalogNyObject(self, p_ob):
        try: self.getCatalogTool().uncatalog_object(self.__buildCatalogPath(p_ob))
        except: self.log_current_error()

    def recatalogNyObject(self, p_ob):
        try:
            catalog_tool = self.getCatalogTool()
            l_ob_path = self.__buildCatalogPath(p_ob)
            catalog_tool.uncatalog_object(l_ob_path)
            catalog_tool.catalog_object(p_ob, l_ob_path)
        except:
            self.log_current_error()

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
            l_results = self.safe_getobjects(self.__eliminateDuplicates(self.findCatalogedObjects(p_query, p_path, lang)))
        else:
            l_results = self.safe_getobjects(self.__eliminateDuplicates(self.findCatalogedObjectsByGenericQuery(p_query)))
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
        l_results = self.safe_getobjects(l_results)
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
        l_results = self.safe_getobjects(l_results)
        return l_results

    # This function is similar to getCatalogedObjects, but also checks for view permission on objects
    def getCatalogedObjectsCheckView(self, meta_type=None, approved=0, howmany=-1, sort_on='releasedate', sort_order='reverse', has_local_role=0, **kwargs):
        l_results = []
        l_filter = {}
        l_filter = {'submitted': 1} #only submitted items
        if approved: l_filter['approved'] = 1
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
            l_objects = self.safe_getobjects(l_results)
            return [obj for obj in l_objects if getSecurityManager().checkPermission(view, obj)]
        else:
            if howmany > len(l_results):
                howmany = len(l_results)
            l_temp = l_results[:howmany]
            l_all = len(l_results)
            l_objects = self.safe_getobjects(l_temp)
            l_output = []
            l_counter = howmany
            while l_counter < l_all + howmany:
                l_output.extend([obj for obj in l_objects if getSecurityManager().checkPermission(view, obj)])
                if len(l_output) >= howmany:
                    l_output = l_output[:howmany]
                    break
                else:
                    l_temp = l_results[l_counter:l_counter+howmany]
                    l_counter = l_counter + howmany
                    l_objects = self.safe_getobjects(l_temp)
            return l_output

    def latest_visible_uploads(self, meta_type=None):
        """ Generator that yields latest uploaded object viewable by user. """
        filters = {'submitted': 1, 'approved': 1, 'sort_on': 'releasedate',
                   'sort_order': 'reverse'}
        if meta_type:
            filters['meta_type'] = self.utConvertToList(meta_type)
        else:
            filters['meta_type'] = self.searchable_content
        check_perm = getSecurityManager().checkPermission

        # Performance trick: First filter top level objects where user
        # has access and only search by those paths
        paths = []
        top_level = self.getSite().objectValues(self.searchable_content)
        paths = [ofs_path(ob) for ob in top_level if check_perm(view, ob)]
        if not paths:
            return
        else:
            filters['path'] = paths

        all_brains = self.__searchCatalog(filters)

        for brain in all_brains:
            try:
                obj = brain.getObject()
            except Exception:
                continue
            else:
                if check_perm(view, obj):
                    yield obj

    #Monkey patch
    def getCatalogedMapObjects(self, meta_type=None, approved=0, howmany=-1, sort_on='releasedate', sort_order='reverse', has_local_role=0, **kwargs):
        from AccessControl.User import nobody
        from AccessControl.SecurityManagement import newSecurityManager
        auth_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        newSecurityManager(None, nobody)

        l_results = []
        l_filter = {}
        l_filter = {'submitted': 1} #only submitted items
        if approved: l_filter['approved'] = 1
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
            l_objects = self.safe_getobjects(l_results)
            return [obj for obj in l_objects if getSecurityManager().checkPermission(view, obj)]
        else:
            if howmany > len(l_results):
                howmany = len(l_results)
            l_temp = l_results[:howmany]
            l_all = len(l_results)
            l_objects = self.safe_getobjects(l_temp)
            l_output = []
            l_counter = howmany
            while len(l_temp) >= 0:
                l_output.extend([obj for obj in l_objects if getSecurityManager().checkPermission(view, obj)])
                if len(l_output) >= howmany:
                    return l_output[:howmany]
                else:
                    l_temp = l_results[l_counter:l_counter+howmany]
                    l_counter = l_counter + howmany
                    l_objects = self.safe_getobjects(l_temp)
        newSecurityManager(None, auth_user)

    def getCatalogedUnsubmittedObjects(self, meta_type=None):
        """
        Returns a list with all I{brain} objects that are not submitted.
        """
        l_filter = {'submitted': 0}
        if meta_type: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        return self.safe_getobjects(self.__searchCatalog(l_filter))

    def getCatalogedBrains(self, meta_type=None):
        """
        Returns a list with all I{brain} objects in the catalog.
        """
        l_filter = {}
        if meta_type is not None: l_filter['meta_type'] = self.utConvertToList(meta_type)
        else: l_filter['meta_type'] = self.searchable_content
        return self.__searchCatalog(l_filter)

    def query_brains_ex(self, meta_type=None, q=None, lang=None, path=None,
                              howmany=-1, **kwargs):
        l_results = []

        l_filter = {'submitted': 1} #only submitted items

        if meta_type:
            l_filter['meta_type'] = self.utConvertToList(meta_type)
        else:
            l_filter['meta_type'] = self.searchable_content

        if path is not None:
            l_filter['path'] = path

        for key, value in kwargs.items():
            if value is not None:
                l_filter[key] = value

        if q is not None:
            if lang is not None:
                l_filter['objectkeywords_%s' % lang] = q
                l_results.extend(self.__searchCatalog(l_filter))
                l_filter.pop('objectkeywords_%s' % lang)
            l_filter['PrincipiaSearchSource'] = q

        l_results.extend(self.__searchCatalog(l_filter))

        if howmany != -1:
            l_results = l_results[:howmany]
        return l_results

    def query_objects_ex(self, meta_type=None, q=None, lang=None, path=None, howmany=-1, **kwargs):
        l_results = self.query_brains_ex(meta_type, q, lang, path, howmany, **kwargs)
        return self.safe_getobjects(l_results)

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
        return self.safe_getobjects(l_results)

    def getCommentedObjects(self):
        paths = set()
        for brain in self.__searchCatalog({'meta_type': 'Naaya Comment'}):
            pieces = brain.getPath().split('/')
            # we expect brain.getPath() to returns: `comentable-object-path`/.comments/`comment-numeric-id`
            assert pieces[-1].isdigit()
            assert pieces[-2] == '.comments'
            paths.add('/'.join(pieces[:-2]))    #get commentable-object-path
        return [self.unrestrictedTraverse(path, None) for path in paths]

    def getLatestComments(self, path, limit=0):
        brains = self.__searchCatalog({'meta_type': 'Naaya Comment',
                                        'path': path,
                                        'sort_on': 'releasedate',
                                        'sort_order': 'reverse'})
        if limit:
            brains = brains[:limit]
        return self.safe_getobjects(brains)

    def getCatalogCheckedOutObjects(self):
        return self.safe_getobjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'checkout': 1}))

    def getNotCheckedObjects(self):
        return self.safe_getobjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'validation_status': 0}))

    def getCheckedOkObjects(self):
        return self.safe_getobjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'validation_status': 1}))

    def getCheckedNotOkObjects(self):
        return self.safe_getobjects(self.__searchCatalog({'meta_type': self.searchable_content, 'submitted': 1, 'validation_status': -1}))
