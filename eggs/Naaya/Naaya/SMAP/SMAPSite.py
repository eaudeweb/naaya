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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports

#Zope imports
from Globals                                    import InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

#Product imports
from constants                                      import *
from Products.NaayaBase.constants                   import *
from Products.NaayaContent                          import *
from Products.Naaya.constants                       import *
from Products.NaayaCore.constants                   import *
from Products.NaayaCore.ProfilesTool.ProfileMeta    import ProfileMeta
from Products.Naaya.NySite                          import NySite
from Products.NaayaCore.managers.utils              import utils, file_utils, batch_utils
from Products.RDFCalendar.RDFCalendar               import manage_addRDFCalendar
from Products.RDFSummary.RDFSummary                 import manage_addRDFSummary
from managers.utils                                 import *
from tools.SyncerTool.SyncerTool                    import manage_addSyncerTool
from Products.NaayaForum.NyForum                    import manage_addNyForum
from tools.constants                                import *
from Products.NaayaCore.managers.xmlrpc_tool        import XMLRPCConnector
from Products.NaayaCore.managers.paginator          import ObjectPaginator


manage_addSMAPSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addSMAPSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, SMAPSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    self._getOb(id).createSMAPPortalTools()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class SMAPSite(NySite, ProfileMeta):
    """ """

    meta_type = METATYPE_SMAPSITE
    icon = 'misc_/SMAP/Site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)

###
# Default 'Naaya' configuration
###############################
    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #load site skeleton - configuration
        self.loadSkeleton(join(SMAP_PRODUCT_PATH, 'skel'))

        #custom indexes
        try:    self.getCatalogTool().manage_addIndex('resource_area', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass
        try:    self.getCatalogTool().manage_addIndex('resource_focus', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass
        try:    self.getCatalogTool().manage_addIndex('resource_area_exp', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass
        try:    self.getCatalogTool().manage_addIndex('resource_focus_exp', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass
        try:    self.getCatalogTool().manage_addIndex('resource_country', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')
        self.manage_delObjects('info')
        self.getPortletsTool().manage_delObjects('topnav_links')

        #set default 'Main topics'
        try:    self.getPropertiesTool().manageMainTopics(['fol120392', 'fol657555', 'fol112686', 'fol034934', 'test1'])
        except: pass

        #set portal index's right portlets
        self.getPortletsTool().set_right_portlets_locations('', ['portlet_rdfcalendar'])

        #default Forum instance
        manage_addNyForum(self, id=ID_FORUM, title=TITLE_FORUM)

        #default RDF Calendar settings
        manage_addRDFCalendar(self, id=ID_RDFCALENDAR, title=TITLE_RDFCALENDAR, week_day_len=1)
        #to be done after add
        #rdfcalendar_ob = self._getOb(ID_RDFCALENDAR)
        #manage_addRDFSummary(rdfcalendar_ob, 'events', 'Events',
        #                     'http://smap.ewindows.eu.org/events/index_rdf', '', 'no')
        #rdfcal_ob = self._getOb(ID_RDFCALENDAR)
        #rdfcal_ob._getOb('events').update()
        country_folder = self._getOb('fol112686')
        country_folder.manage_role('Authenticated', ['Naaya - Add Naaya Contact objects', 'Naaya - Add Naaya Event objects', 'Naaya - Add Naaya Document objects', 'Naaya - Add Naaya Extended File objects', 'Naaya - Add Naaya File objects', 'Naaya - Access administrative area', 'Naaya - Add Naaya Folder objects', 'Naaya - Add Naaya GeoPoint objects', 'Naaya - Add Naaya Media File objects', 'Naaya - Add Naaya News objects', 'Naaya - Add Naaya Pointer objects', 'Naaya - Add Naaya SMAP Expert objects', 'Naaya - Add Naaya SMAP Project objects'])

        #portal_map custom index
        custom_map_index = self.futRead(join(SMAP_PRODUCT_PATH, 'skel', 'others', 'map_index.zpt'))
        portal_map = self.getGeoMapTool()
        manage_addPageTemplate(portal_map, id='map_index', title='', text='')
        map_index = portal_map._getOb(id='map_index')
        map_index.pt_edit(text=custom_map_index, content_type='')


    security.declarePrivate('createSMAPPortalTools')
    def createSMAPPortalTools(self):
        """ """
        manage_addSyncerTool(self, dest_server='', username='', password='')

###
# Administration pages
######################
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_updates_html')
    def admin_updates_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_updates')

###
# Layer over selection lists
############################
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addreflist')
    def admin_addreflist(self, id='', title='', description='', assoc_list='', REQUEST=None):
        """ """
        if assoc_list: id = assoc_list
        self.getPortletsTool().manage_addRefList(id, title, description)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_reflists_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'testRefListExist')
    def testRefListExist(self, id):
        """ """
        for item in self.getPortletsTool().getRefLists():
            if item.id == id: return 1
        return 0

    security.declarePublic('getCountriesList')
    def getCountriesList(self):
        """ Return the selection list for countries """
        return self.getPortletsTool().getRefListById('countries').get_list()

    security.declarePublic('getCountryName')
    def getCountryName(self, id):
        """ Return the title of an item for the selection list for countries """
        try:
            return self.getPortletsTool().getRefListById('countries').get_item(id).title
        except:
            return ''

    security.declarePublic('getPrioritiesTypesList')
    def getPrioritiesTypesList(self):
        """ Return Projects selection list for priorities types """
        return self.getPortletsTool().getRefListById('priorities_types').get_list()

    security.declarePublic('getPriorityTitle')
    def getPriorityTitle(self, id):
        """ Return the title of an item for the selection list for priorities types """
        try:
            return self.getPortletsTool().getRefListById('priorities_types').get_item(id).title
        except:
            return ''

    security.declarePublic('getFocusesTypesList')
    def getFocusesTypesList(self, priority_id):
        """ Return the selection list for focuses types for a given project """
        focus_list_id = "focuses_%s" % priority_id[:3]
        try:
            return self.getPortletsTool().getRefListById(focus_list_id.lower()).get_list()
        except:
            return []

    security.declarePublic('getExpPrioritiesTypesList')
    def getExpPrioritiesTypesList(self):
        """ Return Experts selection list for priorities types"""
        return self.getPortletsTool().getRefListById('priorities_types_exp').get_list()

    security.declarePublic('getExpPriorityTitle')
    def getExpPriorityTitle(self, id):
        """ Return the title of an item for the selection list for priorities types """
        try:
            return self.getPortletsTool().getRefListById('priorities_types_exp').get_item(id).title
        except:
            return ''

    security.declarePublic('getExpFocusesTypesList')
    def getExpFocusesTypesList(self, priority_id):
        """ Return the selection list for focuses types for a given project """
        focus_list_id = "focuses_%s_exp" % priority_id[:3]
        try:
            return self.getPortletsTool().getRefListById(focus_list_id.lower()).get_list()
        except:
            return []

    def getSessionMainTopics(self, topic):
        """ """
        return [x.split('|@|')[0] for x in self.utConvertToList(topic)]

    def checkSessionSubTopics(self, maintopic, subtopic, session):
        """ """
        for sb in self.utConvertToList(session):
            if sb == '%s|@|%s' % (maintopic, subtopic):
                return True
        return False

    security.declarePublic('getFocusTitle')
    def getFocusTitle(self, focus_id, priority_area_id):
        """ Return the title of an item for the selection list for focuses types """
        focus_list_id = "focuses_%s" % priority_area_id[:3]
        try:
            return self.getPortletsTool().getRefListById(focus_list_id.lower()).get_item(focus_id).title
        except:
            return ''

    security.declarePublic('getExpFocusTitle')
    def getExpFocusTitle(self, focus_id, priority_area_id):
        """ Return the title of an item for the selection list for focuses types """
        focus_list_id = "focuses_%s_exp" % priority_area_id[:3]
        try:
            return self.getPortletsTool().getRefListById(focus_list_id.lower()).get_item(focus_id).title
        except:
            return ''

###
# Objects getters
#################

    def getSkinFilesPath(self): return self.getLayoutTool().getSkinFilesPath()

    security.declarePublic('getSyncerTool')
    def getSyncerTool(self): return self._getOb(ID_SYNCERTOOL)

###
# Projects/Experts search
#########################

    security.declarePublic('parametrize_url')
    def parametrize_url(self, url, page=0, free_text='', focus=[], country=[], priority_area=[], exp_changed='', prj_changed='', skey='', rkey=''):
        """ """
        from ZTUtils import make_query
        params = {}
        params['page'] = page
        if free_text:
            params['free_text'] = free_text
        if focus:
            params['focus'] = focus
        if country:
            params['country'] = country
        if priority_area:
            params['priority_area'] = priority_area
        if exp_changed:
            params['exp_changed'] = exp_changed
        if prj_changed:
            params['prj_changed'] = prj_changed
        if skey:
            params['skey'] = skey
        if rkey:
            params['rkey'] = rkey
        query = make_query(params)
        return '%s?%s' % (url, query)

    security.declarePublic('paggingContent')
    def paggingContent(self, content):
        return ObjectPaginator(content, num_per_page=10, orphans=6)

    security.declarePublic('searchExperts')
    def searchExperts(self, priority_area='', focus=[], country='', free_text='', skey='', rkey=0, perform_search='', REQUEST=None):
        """ """
        country = self.utConvertToList(country)
        focus = self.utConvertToList(focus)

        query = ''
        res = []
        lang = self.gl_get_selected_language()
        _focus = ["%s|@|%s" % (priority_area, f) for f in self.utConvertToList(focus)]
        if perform_search:
            query = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSMAPEXPERT], approved=1'
            if len(priority_area) > 0 and priority_area != 'all':
                query += ', resource_area_exp=priority_area'
            if len(_focus) > 0:
                focuses = " or ".join(_focus)
                focuses = self.utStrEscapeForSearch(focuses)
                query += ', resource_focus_exp=focuses'
            if len(country) > 0:
                countries = " or ".join(country)
                countries = self.utStrEscapeForSearch(countries)
                query += ', resource_country=countries'
            if free_text:
                free_text = self.utStrEscapeForSearch(free_text)
                query += ', objectkeywords_%s=free_text' % lang
            query += ')'
            res.extend(eval(query))

        return self.get_archive_listing(self.sorted_archive(res, skey, rkey))

    security.declarePublic('searchProjects')
    def searchProjects(self, priority_area='', focus=[], country='', free_text='', skey='', rkey=0, perform_search='', REQUEST=None):
        """ """
        country = self.utConvertToList(country)
        focus = self.utConvertToList(focus)

        query = ''
        res = []
        lang = self.gl_get_selected_language()
        _focus = ["%s|@|%s" % (priority_area, f) for f in self.utConvertToList(focus)]
        if perform_search:
            query = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSMAPPROJECT], approved=1'
            if len(priority_area) > 0 and priority_area != 'all':
                query += ', resource_area=priority_area'
            if len(_focus) > 0:
                focuses = " or ".join(_focus)
                focuses = self.utStrEscapeForSearch(focuses)
                query += ', resource_focus=focuses'
            if len(country) > 0:
                countries = " or ".join(country)
                countries = self.utStrEscapeForSearch(countries)
                query += ', resource_country=countries'
            if free_text:
                free_text = self.utStrEscapeForSearch(free_text)
                query += ', objectkeywords_%s=free_text' % lang
            query += ')'
            res.extend(eval(query))

        return self.get_archive_listing(self.sorted_archive(res, skey, rkey))

    def sorted_archive(self, p_objects=[], skey='', rkey=0):
        """ Return sorted projects """
        results = []
        if not skey or skey == 'releasedate':
            p_objects.sort(lambda x,y: cmp(y.releasedate, x.releasedate) \
                or cmp(x.sortorder, y.sortorder))
            if not rkey: p_objects.reverse()
            results.extend(p_objects)
        else:
            if rkey: rkey=1
            l_objects = utSortObjsByLocaleAttr(p_objects, skey, rkey, self.gl_get_selected_language())
            results.extend(l_objects)
        return results

    def get_archive_listing(self, p_objects):
        """ """
        results = []
        select_all, delete_all, flag = 0, 0, 0
        for x in p_objects:
            del_permission = x.checkPermissionDeleteObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission and flag == 0:
                select_all, delete_all, flag = 1, 1, 1
            if edit_permission and flag == 0:
                flag, select_all = 1, 1
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results.append((del_permission, edit_permission, x))
        return (select_all, delete_all, results)

    security.declarePublic('stripAllHtmlTags')
    def stripAllHtmlTags(self, p_text):
        """ """
        return utils().utStripAllHtmlTags(p_text)

    security.declareProtected(view, 'country_search')
    def country_search(self, context='', country_code='', REQUEST=None, RESPONSE=None):
        """ Search projects by country search form """
        return self.getFormsTool().getContent({'here': context, 'country_code': [country_code]}, 'projects_search')

    security.declareProtected(view, 'country_search_experts')
    def country_search_experts(self, context='', country_code='', REQUEST=None, RESPONSE=None):
        """ Search projects by country search form """
        return self.getFormsTool().getContent({'here': context, 'country_code': [country_code]}, 'experts_search')

    security.declareProtected(view, 'administration_map_html')
    def administration_map_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'folder_administration_map')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_map')
    def admin_folder_map(self, folder, center_map='', zoom_map='', width_map='', height_map='', REQUEST=None):
        """ """
        object = self.restrictedTraverse(folder, None)
        if object:
            center_map = center_map or 'Palermo, Italy'
            zoom_map = zoom_map or 11
            width_map = width_map or 600
            height_map = height_map or 300
            object.manage_changeProperties({'center_map' : center_map, 'zoom_map': zoom_map, 'width_map': width_map, 'height_map': height_map})
            object._p_changed = 1
        if REQUEST: return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

###
# Folder export/import
######################
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'generatePath')
    def generatePath(self, context='', res=''):
        """ """
        if context.meta_type != METATYPE_SMAPSITE:
            if res:
                l_res = '%s/%s' % (context.id, res)
            else:
                l_res = context.id
            parent_ob = context.getParentNode()
            res = self.generatePath(parent_ob, l_res)
        return res

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'export_html')
    def export_html(self, url='', REQUEST=None, RESPONSE=None):
        """ """
        context = self.unrestrictedTraverse(url, None)
        if context: return self.getFormsTool().getContent({'here': context}, 'folder_impex_export')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'import_html')
    def import_html(self, url='', REQUEST=None, RESPONSE=None):
        """ """
        context = self.unrestrictedTraverse(url, None)
        if context: return self.getFormsTool().getContent({'here': context}, 'folder_impex_import')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'folder_import')
    def folder_import(self, folder='', source='file', file='', url='', REQUEST=None):
        """ """
        context = self.unrestrictedTraverse(folder, None)
        if context:
            context.manage_import(source, file, url)
            if REQUEST: return REQUEST.RESPONSE.redirect('import_html?url=%s' % folder)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'update_html')
    def update_html(self, url='', REQUEST=None, RESPONSE=None):
        """ """
        context = self.unrestrictedTraverse(url, None)
        if context: return self.getFormsTool().getContent({'here': context}, 'folder_impex_update')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'commit_html')
    def commit_html(self, url='', REQUEST=None, RESPONSE=None):
        """ """
        context = self.unrestrictedTraverse(url, None)
        if context: return self.getFormsTool().getContent({'here': context}, 'folder_impex_commit')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getFolderishExportedData')
    def getFolderishExportedData(self):
        """ """
        r = []
        ra = r.append
        ra('<?xml version="1.0" encoding="utf-8"?>')
        ra('<export xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="%s">' % self.nyexp_schema)
        for x in self.getSite().get_containers():
            ra(x.export_this(folderish=1))
        ra('</export>')
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=%s.nyexp' % self.id)
        return ''.join(r)

###
# Updates
######################
    security.declareProtected(view_management_screens, 'updateExperts')
    def updateExperts(self):
        """ expert object is associated to more than one category (priority areas/main topics of expertise) """
        experts = self.getCatalogedObjects(meta_type=[METATYPE_NYSMAPEXPERT])
        for expert in experts:
            buf = []
            for k in expert.subtopics:
                buf.append('%s|@|%s' % (expert.maintopics, k))
            expert.subtopics = buf
            expert.maintopics = self.utConvertToList(expert.maintopics)
            expert._p_changed = 1
        print 'done'

    security.declareProtected(view_management_screens, 'updateProjects')
    def updateProjects(self):
        """ project object is associated to more than one category (priority areas/main topics of expertise) """
        info = 0
        projects = self.getCatalogedObjects(meta_type=[METATYPE_NYSMAPPROJECT])
        for project in projects:
            buf = []
            if type(project.priority_area) != type([]):
                info += 1
                for k in project.focus:
                    buf.append('%s|@|%s' % (project.priority_area, k))
                project.focus = buf
                project.priority_area = self.utConvertToList(project.priority_area)
                project._p_changed = 1
        print 'Done. %s objects updated.' % info

InitializeClass(SMAPSite)
