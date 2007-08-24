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
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Gabriel Agu
# Miruna Badescu
# Alin Voinea

#Python imports
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED, BadZipfile

#Zope imports
from zExceptions import BadRequest
from ZPublisher.HTTPRequest import FileUpload
from Globals                                    import InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view

#Zope imports
from Products.RDFCalendar.RDFCalendar               import manage_addRDFCalendar
from Products.RDFSummary.RDFSummary                 import manage_addRDFSummary
try:
    from Products.NaayaCore.GeoMapTool.GeoMapTool       import manage_addGeoMapTool
    GM_INSTALLED = 1
except ImportError:
    GM_INSTALLED = 0

#Product imports
from constants                                      import *
from Products.NaayaBase.constants                   import *
from Products.NaayaContent                          import *
from Products.Naaya.constants                       import *
from Products.NaayaCore.constants                   import *
from Products.Naaya.NySite                          import NySite
from Products.NaayaCore.managers.utils              import utils


manage_addEnviroWindowsSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addEnviroWindowsSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, EnviroWindowsSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class EnviroWindowsSite(NySite):
    """ """

    meta_type = METATYPE_ENVIROWINDOWSSITE
    icon = 'misc_/EnviroWindows/Site.gif'

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
        self.loadSkeleton(join(ENVIROWINDOWS_PRODUCT_PATH, 'skel'))

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

        #default RDF Calendar settings
        manage_addRDFCalendar(self, id=ID_RDFCALENDAR, title=TITLE_RDFCALENDAR, week_day_len=1)
        rdfcalendar_ob = self._getOb(ID_RDFCALENDAR)
        #TODO: to change the RDF Summary url maybe
        manage_addRDFSummary(rdfcalendar_ob, 'example', 'Example',
                             'http://smap.ewindows.eu.org/portal_syndication/events_rdf', '', 'no')
        rdfcal_ob = self._getOb(ID_RDFCALENDAR)
        #rdfcal_ob._getOb('example').update()

        #dynamic property for folder: tooltip
        dynprop_tool = self.getDynamicPropertiesTool()
        dynprop_tool.manage_addDynamicPropertiesItem(id=METATYPE_FOLDER, title=METATYPE_FOLDER)
        dynprop_tool._getOb(METATYPE_FOLDER).manageAddDynamicProperty(id='show_contributor_request_role', name='Allow users enrolment here?', type='boolean')

        if GM_INSTALLED:
            manage_addGeoMapTool(self)


    security.declarePublic('getBreadCrumbTrail')
    def getBreadCrumbTrail(self, REQUEST):
        """ generates the breadcrumb trail """
        root = self.utGetROOT()
        breadcrumbs = []
        vRoot = REQUEST.has_key('VirtualRootPhysicalPath')
        PARENTS = REQUEST.PARENTS[:]
        PARENTS.reverse()
        if vRoot:
             root = REQUEST.VirtualRootPhysicalPath
             PARENTS = PARENTS[len(root)-1:]
        PARENTS.reverse()
        for crumb in PARENTS:
            if crumb.meta_type == self.meta_type:
                break
            breadcrumbs.append(crumb)
        breadcrumbs.reverse()
        return breadcrumbs

    security.declarePublic('stripAllHtmlTags')
    def stripAllHtmlTags(self, p_text):
        """ """
        return utils().utStripAllHtmlTags(p_text)

################
# Epoz related #
################
    security.declareProtected(view, 'insertrelativelink_html')
    def insertrelativelink_html(self, REQUEST=None, RESPONSE=None):
        """
        Opens a page with site map and insert a relative link in the wysiwyg widget editor.
        """
        return self.getFormsTool().getContent({'here': self}, 'site_insertrelativelink')

##############################
# Layer over selection lists #
##############################
#TODO: Review and make more generic: this part was built for SMAP

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

#####################################################
# ENVIROWINDOWS functions loaded for compatibility  #
#####################################################

    def getPendingAnnouncements(self, container=None):
        #returns a list with the draft NYNews objects from the specified folder(container)
        if container is None or container == self:
            return self.getCatalogedObjectsA(meta_type=METATYPE_NYNEWS, approved=0)
        else:
            sector = container.id
            return self.getCatalogedObjects(meta_type=METATYPE_NYNEWS, approved=0, sector=sector)

    def getAnnouncementsFrontPage(self, howmany=None):
        #returns a list with latest approved NYNews objects from the specified folder(container)
        #the number of objects can be set by modifing the property 'number_announcements'
        if howmany is None: howmany = -1
        return self.getCatalogedObjects(meta_type=METATYPE_NYNEWS, approved=1, howmany=howmany, topstory=1)

    def getAnnouncements(self, container=None, howmany=None):
        #returns a list with latest approved EWNews objects from the specified folder(container)
        #the number of objects can be set by modifing the property 'number_announcements'
        if howmany is None: howmany = -1
        if container is None: sector = None
        elif container == self: sector = None
        else:
            l_top_container = container
            while l_top_container.getParentNode() != self:
                l_top_container = l_top_container.getParentNode()
            sector = l_top_container.id
        if sector:
            return self.getCatalogedObjects(meta_type=METATYPE_NYNEWS, approved=1, howmany=howmany, sector=sector)
        else:
            return self.getCatalogedObjects(meta_type=METATYPE_NYNEWS, approved=1, howmany=howmany)

#####################################################
# SMAP functions loaded for backwards compatibility #
#####################################################
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
        projects = self.getCatalogedObjects(meta_type=[METATYPE_NYSMAPPROJECT])
        for project in projects:
            buf = []
            for k in project.focus:
                buf.append('%s|@|%s' % (project.priority_area, k))
            project.focus = buf
            project.priority_area = self.utConvertToList(project.priority_area)
            project._p_changed = 1
        print 'done'

    #
    # Upload/download folder items from/to zip archive
    #
    security.declareProtected(view, 'getDocuments')
    def getDocuments(self, path, meta_type=''):
        """ Returns object values of given meta_type in given path.
        """
        meta_type = meta_type or METATYPE_NYEXFILE
        folder = self.getObjectByPath(path)
        if not folder: return []
        return folder.objectValues(meta_type)
    
    security.declareProtected(view, 'getObjectByPath')
    def getObjectByPath(self, path):
        """ Returns object at given path
        """
        res = self.unrestrictedTraverse(path)
        return res
    
    security.declareProtected(view, 'zip_upload_html')
    def zip_upload_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_zipupload')
    
    security.declareProtected(view, 'zip_download_html')
    def zip_download_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_zipdownload')

    security.declarePrivate('zip_redirect')
    def zip_redirect(self, path, errors="", RESPONSE=None):
        """ Redirect RESPONSE to given path and add errors if exists to session.
        """
        if isinstance(errors, str):
            errors = [errors]
        if not RESPONSE:
            return errors
        
        if errors:
            self.setSessionErrors(errors)
        RESPONSE.redirect(path)
    
    security.declareProtected(view, 'zipDownloadDocuments')
    def zipDownloadDocuments(self, REQUEST=None, RESPONSE=None):
        """ Return a zip archive content as a session response.
        """
        if not (REQUEST and RESPONSE):
            return ""
        
        path = REQUEST.form.get('path', '')
        doc_ids = REQUEST.form.get('ids', [])
        folder = self.getObjectByPath(path)
        if not folder:
            self.zip_redirect(path, "Invalid folder path", RESPONSE)
        
        RESPONSE.setHeader('Content-Type', 'application/x-zip-compressed')
        RESPONSE.setHeader('Content-Disposition', 
                           'attachment; filename=%s.zip' % folder.getId())
        return self._zipDownloadDocuments(path, doc_ids)
    
    security.declarePrivate('_zipDownloadDocuments')
    def _zipDownloadDocuments(self, path, doc_ids):
        """ Create and return a zip archive from folder items defined by 
        doc_ids.
        
        @path: folder relative path
        @doc_ids: folder items
        returns a zip archive content
        """
        zip_buffer = StringIO()
        zip_file = ZipFile(zip_buffer, 'w', ZIP_DEFLATED)
        
        for doc_id in doc_ids:
            doc = self.getObjectByPath(path + "/" + doc_id)
            if not doc: 
                continue
            
            doc_name = getattr(doc, 'downloadfilename', "") or doc_id
            namelist = zip_file.namelist()
            if doc_name in namelist:
                doc_name = "%s-%s" % (len(namelist), doc_name)

            doc_data = getattr(doc.getFileItem(), 'data', None)
            
            if not isinstance(doc_data, str):
                data_buffer = StringIO()
                while doc_data is not None:
                    data_buffer.write(doc_data.data)
                    doc_data = doc_data.next
                doc_data = data_buffer.getvalue()
                
            if not doc_data:
                continue
            zip_file.writestr(doc_name, doc_data)
        
        zip_file.close()
        return zip_buffer.getvalue()
    
    security.declareProtected(view, 'zipUploadDocuments')
    def zipUploadDocuments(self, REQUEST=None, RESPONSE=None):
        """ Call zip importer and redirect to folder index.
        """
        if not (REQUEST and RESPONSE):
            return ""
        
        path = REQUEST.form.get('path', '')
        upload_file = REQUEST.form.get('upload_file', None)
        
        folder = self.getObjectByPath(path)
        if not folder:
            self.zip_redirect(path, "Invalid folder path", RESPONSE)
        
        try:
            errors = self._zipUploadDocuments(folder, upload_file)
        except ZipUploadError, error:
            self.zip_redirect(path, error, RESPONSE)
        else:
            self.zip_redirect(path, errors, RESPONSE)
    
    security.declarePrivate("_zipUploadDocuments")
    def _zipUploadDocuments(self, folder, upload_file):
        """ Create objects in given folder from upload_file zip archive.
        
        @folder: a NyFolder instance;
        @upload_file: a FileUpload instance;
        returns occured errors.
        """
        try:
            zip_file = ZipFile(upload_file)
        except BadZipfile, error:
            raise ZipUploadError(error)
        except IOError, error:
            raise ZipUploadError("Invalid archive: %s" % error)
        except Exception, error:
            raise ZipUploadError(error)
        
        namelist = zip_file.namelist()
        folderish = [name for name in namelist if '/' in name]
        if folderish: 
            raise ZipUploadError("Invalid archive: folderish "
                                 "structure not supported.")
        
        errors = []
        for zinfo in zip_file.filelist:
            filename = zinfo.filename
            filesize = zinfo.file_size
            # Handle CRC error
            try:
                file_data = zip_file.read(filename)
            except BadZipfile, error:
                errors.append("Could not add file %s: %s" % (filename, error))
                continue
            
            headers = {'content-length': filesize}
            file_buffer = StringIO(file_data)
            
            fs = SimpleFieldStorage(file_buffer, filename, headers)
            file_obj = FileUpload(fs)
            try:
                folder.addNyExFile(title=filename, file=file_obj)
            except BadRequest, error:
                errors.append("Could not add file %s: %s" % (filename, error))
                continue
        
        return errors

InitializeClass(EnviroWindowsSite)

#
# Zip utils  
#
class ZipUploadError(Exception):
    pass

class SimpleFieldStorage(object):
    """ A simple FieldStorage to hold a file.
    """
    def __init__(self, file, filename, headers):
        self.file = file
        self.filename = filename
        self.headers = headers
