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

#Product imports
from constants                                      import *
from Products.NaayaBase.constants                   import *
from Products.NaayaContent                          import *
from Products.Naaya.constants                       import *
from Products.NaayaCore.constants                   import *
from Products.Naaya.NySite                          import NySite
from Products.NaayaCore.managers.utils              import utils
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker
from Products.Naaya.NyFolder import addNyFolder


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

    security.declareProtected(view_management_screens, 'addConsultationDynProp')
    def addConsultationDynProp(self):
        dynprop_tool = self.getDynamicPropertiesTool()
        try:
            dynprop_tool.manage_addDynamicPropertiesItem(id=METATYPE_NYCONSULTATION, title=METATYPE_NYCONSULTATION)
            dynprop_tool._getOb(METATYPE_NYCONSULTATION).manageAddDynamicProperty(id='show_contributor_request_role', name='Allow visitors to register as reviewers for this consultation', type='boolean')

            dynprop_tool.manage_addDynamicPropertiesItem(id=METATYPE_NYSIMPLECONSULTATION, title=METATYPE_NYSIMPLECONSULTATION)
            dynprop_tool._getOb(METATYPE_NYSIMPLECONSULTATION).manageAddDynamicProperty(id='show_contributor_request_role', name='Allow visitors to register as reviewers for this consultation', type='boolean')
        except: pass

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

        #dynamic properties for consultation objects
        self.addConsultationDynProp()

        #add survey tool
        try:
            from Products.NaayaSurvey.SurveyTool import manage_addSurveyTool
            manage_addSurveyTool(self)
        except:
            pass

        #create and configure LinkChecker instance
        manage_addLinkChecker(self, ID_LINKCHECKER, TITLE_LINKCHECKER)
        linkchecker_ob = self._getOb(ID_LINKCHECKER)
        linkchecker_ob.manage_edit(proxy='', batch_size=10, catalog_name=ID_CATALOGTOOL)
        linkchecker_ob.manage_addMetaType(METATYPE_NYURL)
        linkchecker_ob.manage_addProperty(METATYPE_NYURL, 'locator')
        for k,v in self.get_content_urls().items():
            linkchecker_ob.manage_addMetaType(k)
            for p in v:
                linkchecker_ob.manage_addProperty(k, p)

    #object getters
    def getLinkChecker(self): return self._getOb(ID_LINKCHECKER, None)
    def getLinkCheckerLastLog(self):
        entries = self.utSortObjsListByAttr(self._getOb(ID_LINKCHECKER).objectValues('LogEntry'), 'date_create', p_desc=1)
        if len(entries) > 0: return entries[0]
        else: return None

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

#################################
# Apply for contribution rigths #
#################################

    #---------- session objects ------
    #manage users
    def setContributorSession(self, name, roles, firstname, lastname, email, password='',
        organisation='', comments='', address='', phone='', title='', description='', fax='', website=''):
        """ put the user information on session """
        self.setSession('contr_firstname', firstname)
        self.setSession('contr_lastname', lastname)
        self.setSession('contr_email', email)
        self.setSession('contr_address', address)
        self.setSession('contr_phone', phone)
        self.setSession('contr_name', name)
        self.setSession('contr_password', password)#??
        self.setSession('contr_organisation', organisation)
        self.setSession('contr_title', title)
        self.setSession('contr_description', description)
        self.setSession('contr_fax', fax)
        self.setSession('contr_website', website)
        self.setSession('contr_roles', roles)
        #self.setSession('contr_domains', domains)  #not used for the moment
        self.setSession('contr_comments', comments)

    def delContributorSession(self):
        """ delete user information from session """
        self.delSession('contr_firstname')
        self.delSession('contr_lastname')
        self.delSession('contr_email')
        self.delSession('contr_address')
        self.delSession('contr_phone')
        self.delSession('contr_name')
        self.delSession('contr_password')#??
        self.delSession('contr_organisation')
        self.delSession('contr_title')
        self.delSession('contr_description')
        self.delSession('contr_fax')
        self.delSession('contr_website')
        self.delSession('contr_roles')
        #self.delSession('contr_domains')
        self.delSession('contr_comments')

    def getSessionContributorFirstname(self, default=''):
        return self.getSession('contr_firstname', default)

    def getSessionContributorLastname(self, default=''):
        return self.getSession('contr_lastname', default)

    def getSessionContributorEmail(self, default=''):
        return self.getSession('contr_email', default)

    def getSessionContributorAddress(self, default=''):
        return self.getSession('contr_address', default)

    def getSessionContributorPhone(self, default=''):
        return self.getSession('contr_phone', default)

    def getSessionContributorName(self, default=''):
        return self.getSession('contr_name', default)

    def getSessionContributorPassword(self, default=''):
        return self.getSession('contr_password', default)

    def getSessionContributorOrganisation(self, default=''):
        return self.getSession('contr_organisation', default)

    def getSessionContributorTitle(self, default=''):
        return self.getSession('contr_title', default)

    def getSessionContributorDescription(self, default=''):
        return self.getSession('contr_description', default)

    def getSessionContributorFax(self, default=''):
        return self.getSession('contr_fax', default)

    def getSessionContributorWebsite(self, default=''):
        return self.getSession('contr_website', default)

    def getSessionContributorRoles(self, default=''):
        return self.getSession('contr_roles', default)

    #def getSessionContributorDomains(self, default=''):
    #    return self.getSession('contr_domains', default)

    def getSessionContributorComments(self, default=''):
        return self.getSession('contr_comments', default)

    security.declareProtected(view, 'hasFolderLocalRoles')
    def hasFolderLocalRoles(self, folder):
        for roles_tuple in folder.get_local_roles():
            for role in roles_tuple[1]:
                if role in ['Administrator', 'Manager']:
                    return True
        return False

    security.declareProtected(view, 'is_logged')
    def is_logged(self, REQUEST):
        """ """
        return REQUEST.AUTHENTICATED_USER.getUserName() != 'Anonymous User'

    #---------- request account & role ------
    security.declareProtected(view, 'sendRequestRoleEmail')
    def sendRequestRoleEmail(self, p_email_data, p_username, p_fullname, p_source, p_role, p_comments):
        """ send email with a request for role """
        if p_role == 'admin':   p_role = 'Administrator'
        if p_role == 'contrib':  p_role = 'Contributor'
        for l_data in p_email_data:
            l_location_path = l_data[1]
            l_location_title = l_data[0]
            l_to = l_data[2]
            obj = self.getEmailTool()._getOb('email_ldap_requestrole')
            l_subject = obj.title
            l_content = obj.body
            l_content = l_content.replace('@@NAME@@', p_fullname)
            l_content = l_content.replace('@@USERNAME@@', p_username)
            l_content = l_content.replace('@@ROLE@@', p_role)
            l_content = l_content.replace('@@SOURCE@@', p_source)
            l_content = l_content.replace('@@LOCATIONPATH@@', l_location_path)
            if len(l_location_path) > 0:
                l_content = l_content.replace('@@LOCATION@@', "the '%s' folder %s" % (l_location_title, l_location_path))
            else:
                l_content = l_content.replace('@@LOCATION@@', l_location_path)
            l_content = l_content.replace('@@COMMENTS@@', p_comments)
            l_content = l_content.replace('@@PORTAL_URL@@', self.getSitePath(0))
            l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
            l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
            self.getEmailTool().sendEmail(l_content, l_to, self.mail_address_from, l_subject)

    security.declareProtected(view, 'sendRequestAccountAndRoleEmail')
    def sendRequestAccountAndRoleEmail(self, p_email_data, p_title, p_name, p_email, p_organisation,
            p_description, p_address, p_phone, p_fax, p_website, p_username, p_comments, p_role):
        """ Sends email with a request for an account and role """
        if p_role == 'admin':   p_role = 'Administrator'
        if p_role == 'contrib':  p_role = 'Contributor'
        for l_data in p_email_data:
            l_location_path = l_data[1]
            l_location_title = l_data[0]
            l_to = l_data[2]
            obj = self.getEmailTool()._getOb('email_requestaccount')
            l_subject = obj.title
            l_content = obj.body
            l_content = l_content.replace('@@ROLE@@', p_role)
            l_content = l_content.replace('@@TITLE@@', p_title)
            l_content = l_content.replace('@@NAME@@', p_name)
            l_content = l_content.replace('@@EMAIL@@', p_email)
            l_content = l_content.replace('@@ORGANISATION@@', p_organisation)
            l_content = l_content.replace('@@DESCRIPTION@@', p_description)
            l_content = l_content.replace('@@ADDRESS@@', p_address)
            l_content = l_content.replace('@@PHONE@@', p_phone)
            l_content = l_content.replace('@@FAX@@', p_fax)
            l_content = l_content.replace('@@WEBSITE@@', p_website)
            l_content = l_content.replace('@@USERNAME@@', p_username)
            l_content = l_content.replace('@@LOCATIONPATH@@', l_location_path)
            if len(l_location_path) > 0:
                l_content = l_content.replace('@@LOCATION@@', "the '%s' folder %s" % (l_location_title, l_location_path))
            else:
                l_content = l_content.replace('@@LOCATION@@', l_location_path)
            l_content = l_content.replace('@@COMMENTS@@', p_comments)
            l_content = l_content.replace('@@PORTAL_URL@@', self.getSitePath(0))
            l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
            l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
            self.getEmailTool().sendEmail(l_content, l_to, self.mail_address_from, l_subject)

    security.declareProtected(view, 'processRequestRole')
    def processRequestRole(self, role, REQUEST=None, RESPONSE=None):
        """ """
        if REQUEST.has_key('cancel'):
            if REQUEST.has_key('return_path'):
                return RESPONSE.redirect(REQUEST['return_path'])
            else:
                return RESPONSE.redirect(self.getSitePath())
        if self.is_logged(REQUEST):
            return RESPONSE.redirect('requestlocations_html?auth=1&role=%s' % role)
        else:
            return RESPONSE.redirect('requestinfo_html?role=%s' % role)

    security.declareProtected(view, 'processRequestAccount')
    def processRequestAccount(self, username='', passwd='', role='', REQUEST=None, RESPONSE=None):
        """ process an existing account """
        _err = []
        if REQUEST.has_key('cancel'):
            if REQUEST.has_key('return_path'):
                return RESPONSE.redirect(REQUEST['return_path'])
            else:
                return RESPONSE.redirect(self.getSitePath())
        site = self.getSite()
        auth_tool = site.getAuthenticationTool()
        if not (username and passwd):
            _err.append("Username and password must be specified")
        auth_tool.credentialsChanged(username, passwd)
        return RESPONSE.redirect('requestinfo_html?acc=1&role=%s' % role)

    security.declareProtected(view, 'processRequestInfo')
    def processRequestInfo(self, username='', password='', confirm='', title='', firstname='', lastname='',
                    email='', address='', phone='', description='', fax='', website='',
                    organisation='', role='', comments='', REQUEST=None, RESPONSE=None):
        """ process the request for a new account """
        if REQUEST.has_key('cancel'):
            if REQUEST.has_key('return_path'):
                return RESPONSE.redirect(REQUEST['return_path'])
            else:
                return RESPONSE.redirect(self.getSitePath())
        self.setContributorSession(username, role, firstname, lastname, email, '',
                    organisation, comments, address, phone, title, description, fax, website)
        try:
            self.getAuthenticationTool().manage_addUser(username, password, confirm, [], [], firstname, lastname, email, strict=1)
        except Exception, error:
            _err = error
        else:
            _err = ''
        if _err:
            self.setSessionErrors(_err)
            return RESPONSE.redirect('requestinfo_html?role=%s' % role)
        else:
            return RESPONSE.redirect('requestlocations_html?role=%s' % role)

    security.declareProtected(view, 'processRequestLocation')
    def processRequestLocation(self, role='', comments='', locationslist=[], REQUEST=None, RESPONSE=None):
        """ Sends notification email(s) to the administrators when people apply for a role
        """
        if REQUEST.has_key('cancel'):
            if REQUEST.has_key('return_path'):
                return RESPONSE.redirect(REQUEST['return_path'])
            else:
                return RESPONSE.redirect(self.getSitePath())
        site = self.getSite()
        auth_tool = site.getAuthenticationTool()

        l_email_data = []
        location_maintainer_email = []
        l_locationslist = self.convertToList(locationslist)
        if len(l_locationslist) > 0:
            for loc in l_locationslist:
                obj = self.getFolderByPath(loc)
                if obj is not None:
                    location_path = obj.absolute_url(0)
                    location_title = obj.title
                    admin_users = site.get_administrator(self)
                    location_maintainer_email = auth_tool.getUsersEmails(admin_users)
                    if len(location_maintainer_email) == 0: location_maintainer_email.append(self.administrator_email)
                    l_email_data.append((location_title, location_path, location_maintainer_email))

            if self.is_logged(REQUEST):
                username = REQUEST.AUTHENTICATED_USER.getUserName()
                user_source = auth_tool.getUserSource(username)
                try:
                    fullname = auth_tool.getUsersFullNames([username])[0]
                except:
                    fullname = ''
                site.getEmailTool().sendRequestRoleEmail(l_email_data, username, fullname, user_source, role, comments)
            else:
                title = self.getSessionContributorTitle()
                firstname = self.getSessionContributorFirstname()
                lastname = self.getSessionContributorLastname()
                email = self.getSessionContributorEmail()
                organisation = self.getSessionContributorOrganisation()
                description = self.getSessionContributorDescription()
                address = self.getSessionContributorAddress()
                phone = self.getSessionContributorPhone()
                fax = self.getSessionContributorFax()
                website = self.getSessionContributorWebsite()
                username = self.getSessionContributorName()
                if username and role:
                    site.getEmailTool().sendRequestAccountAndRoleEmail(l_email_data, title, '%s %s' % (firstname, lastname), email,
                            organisation, description, address, phone, fax, website, username, comments, role)
                    self.delContributorSession()
            return RESPONSE.redirect('messages_html?referer=%s' % REQUEST.URL1)
        return RESPONSE.redirect('requestlocations_html?role=%s' % role)

    security.declareProtected(view, 'createaccount_html')
    def createaccount_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'site_createaccount')

    security.declareProtected(view, 'requestrole_html')
    def requestrole_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'site_requestrole')

    security.declareProtected(view, 'requestlocations_html')
    def requestlocations_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'site_requestlocations')

    security.declareProtected(view, 'requestinfo_html')
    def requestinfo_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self.REQUEST.PARENTS[0]}, 'site_requestinfo')

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
        res = self.unrestrictedTraverse(path, None)
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
        else:
            if not folder.can_be_seen():
                self.zip_redirect(path, "Restricted access", RESPONSE)

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

            doc_name = getattr(doc, 'downloadfilename', "")
            #TODO: Extend toAscii for other charsets
            doc_name = self.toAscii(doc_name)
            doc_name = doc_name.strip() or self.toAscii(doc_id)

            namelist = zip_file.namelist()
            if doc_name in namelist:
                doc_name = "%s-%s" % (len(namelist), doc_name)

            doc_file = doc.getFileItem()
            doc_data = doc_file.get_data(as_string=False)

            if doc_data.is_broken():
                continue
            else:
                doc_data = doc_file.get_data()

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

            filename = filename.decode("utf-8")
            filename = self.toAscii(filename)
            fs = SimpleFieldStorage(file_buffer, filename, headers)
            file_obj = FileUpload(fs)
            try:
                folder.addNyExFile(title=filename, file=file_obj)
            except BadRequest, error:
                errors.append("Could not add file %s: %s" % (filename, error))
                continue

        return errors

    security.declareProtected(view_management_screens, 'update_email_templates')
    def update_email_templates(self):
        """ """
        from os.path import join
        #reload Naaya email templates
        skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
        emailtool_ob = self.getEmailTool()
        email_templates = {'email_requestrole':'Request role'}
        for k, v in email_templates.items():
            content = self.futRead(join(skel_path, 'emails', '%s.txt' % k), 'r')
            email_ob = emailtool_ob._getOb(k, None)
            if email_ob is None:
                emailtool_ob.manage_addEmailTemplate(k, v, content)
            else:
                email_ob.manageProperties(title=email_ob.title, body=content)

        #reload EnviroWindows email templates
        skel_path = join(ENVIROWINDOWS_PRODUCT_PATH, 'skel')
        emailtool_ob = self.getEmailTool()
        email_templates = {'email_createaccount':'Create account notification', 'email_ldap_requestrole':'Request role (LDAP)', 'email_requestaccount':'Request account'}
        for k, v in email_templates.items():
            content = self.futRead(join(skel_path, 'emails', '%s.txt' % k), 'r')
            email_ob = emailtool_ob._getOb(k, None)
            if email_ob is None:
                emailtool_ob.manage_addEmailTemplate(k, v, content)
            else:
                email_ob.manageProperties(title=email_ob.title, body=content)
        return 'done'

    security.declareProtected(view_management_screens, 'update_portal_forms')
    def update_portal_forms(self):
        """ """
        skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
        formstool_ob = self.getFormsTool()
        portal_forms = {'site_admin_users': 'Portal administration - users'}
        for k, v in portal_forms.items():
            content = self.futRead(join(skel_path, 'forms', '%s.zpt' % k), 'r')
            form_ob = formstool_ob._getOb(k, None)
            if form_ob is None:
                formstool_ob.manage_addTemplate(id=k, title=v, file='')
                form_ob = formstool_ob._getOb(k, None)
            form_ob.pt_edit(text=content, content_type='')

        skel_path = join(ENVIROWINDOWS_PRODUCT_PATH, 'skel')
        formstool_ob = self.getFormsTool()
        portal_forms = {'site_requestrole': 'Portal request role', 'site_requestlocations': 'Portal request role form - step 3', 'site_requestinfo': 'Portal request account form - step 2', 'folder_index': 'NyFolder default view', 'site_login': 'Portal login', 'site_createaccount': 'Portal create account form'}
        for k, v in portal_forms.items():
            content = self.futRead(join(skel_path, 'forms', '%s.zpt' % k), 'r')
            form_ob = formstool_ob._getOb(k, None)
            if form_ob is None:
                formstool_ob.manage_addTemplate(id=k, title=v, file='')
                form_ob = formstool_ob._getOb(k, None)
            form_ob.pt_edit(text=content, content_type='')
        return 'done'

    security.declareProtected(view_management_screens, 'update_portal_css')
    def update_portal_css(self):
        """ """
        css_for_request = """/* request role styles */
.request_role {
	font-family: Arial, Helvetica, sans-serif;
	font-size: 1em;

	padding-bottom: 1em;
	background: #fff;
}
.request_role h2 {
	color: #669933;
	font-weight: bold;
	margin: 0;
	padding: 0;
}
.request_role div p {
	border: 1px solid #ddd;
	padding: 0.5em;
}
.request_role .input_submit {
	padding: 0.2em 0.5em;
	border: 1px solid #ccc;
	background: #fafafa;
}
* html .request_role .input_submit {
	padding: 0 !important;
}
.request_role h3 {
	color: #000;
	font-weight: bold;
	font-size: 1em;
	margin: 0;
	padding: 0;
	text-transform: uppercase;
}
* html .request_role form {
	padding: 0;
	margin: 0;
}
.request_role fieldset {
	margin: 0;
	padding: 0;
}
.request_role .existing_acc {
	border-top: 1px solid #eee;
	margin: 0;
	padding: 0;
}
.request_role .nonexisting_acc {
	margin: 0;
	padding: 2em 0 0 0;
}
.request_role .existing_acc p, .request_role .nonexisting_acc p {
	font-size: 0.9em;
	border: none;
	margin: 0;
	padding: 0.4em;
}
.request_role .existing_acc td, .request_role .nonexisting_acc td  {
	padding: 0.4em;
	font-size: 0.9em;
}
.request_role .existing_acc td input, .request_role .nonexisting_acc td input, .request_role .nonexisting_acc td textarea {
	margin-right: 0.3em;
	font-size: 1em;
	color: #555;
	font-family: Arial, Helvetica, sans-serif;
}
.request_role .existing_acc td input, .request_role .nonexisting_acc td input {
	height: 1.4em;
}
.request_role .mandatory {
	color: #990000;
}
.message-error {
	color: #f30;
}
.message-error fieldset {
	border: 1px solid #999 !important;
	color: #f40000;
}
.message-information {
	color: #77b81f;
}
.message-information fieldset {
	border: 1px solid #999 !important;
	color: #77b81f;
}

a.b_download {
float: right;
font-size: 0.70em;
font-size: normal;
text-decoration: none;
padding-right: 0.3em;
}


a.b_download:hover {
text-decoration: underline;
}"""
        layout_tool = self.getLayoutTool()
        for skin in layout_tool.getSkinsList():
            for scheme in skin.getSchemes():
                css_ob = scheme._getOb('style', None)
                if css_ob is not None:
                    content = css_ob.document_src() + '\n' + css_for_request
                    css_ob.pt_edit(text=content, content_type='')
                else:
                    print "css not found for scheme %s" % scheme.id
        return 'done'

    security.declareProtected('Naaya - Add Naaya News objects', 'submit_news')
    def submit_news(self, REQUEST):
        """ Redirects to the appropiate news folder """

        today = self.utGetTodayDate()
        month = str(today.month())
        year = str(today.year())
        month_name= today.Month()

        try:
            #try to get the 'News' folder
            news_folder = self._getOb('News')
        except AttributeError:
            try:
                #if it's not there, try with 'news'
                news_folder = self._getOb('news')
            except AttributeError:
                #if 'news' doesn't work either, create 'News'
                addNyFolder(self, id='news', title='News Bulletin')
                news_folder = self._getOb('news')

        #get year folder, create it if it doesn't exist
        try:
            year_folder = news_folder._getOb(year)
        except AttributeError:
            addNyFolder(news_folder, id=year, title=year)
            year_folder = news_folder._getOb(year)

        #get month folder, create it if it doesn't exist
        try:
            year_folder._getOb(month)
        except AttributeError:
            addNyFolder(year_folder, id=month, title=month_name)

        news_url = '%s/%s/%s/%s/news_add_html' % (self.absolute_url(),
                                                  news_folder.getId(),
                                                  year,
                                                  month)
        self.REQUEST.RESPONSE.redirect(news_url)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'sendMailToContacts')
    def sendMailToContacts(self, subject='', content='', REQUEST=None):
        """ """
        addresses = [contact.email for contact in self.getCatalogedObjectsCheckView(meta_type=['Naaya Contact'])]

        for address in addresses:
            self.getEmailTool().sendEmail(content, address, self.mail_address_from, subject)

        if REQUEST:
            self.setSessionInfo(['Mail sent. (%s)' % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_contacts_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_contacts_html')
    def admin_contacts_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_contacts')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkchecker_html')
    def admin_linkchecker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkchecker')

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
