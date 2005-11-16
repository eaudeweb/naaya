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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from urlparse import urlparse

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.constants import *
from Products.NaayaNetRepository.constants import *
from Products.HelpDeskAgent.HelpDesk import manage_addHelpDesk
from Products.NaayaGlossary.constants import *
from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre

manage_addCHMSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addCHMSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, CHMSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class CHMSite(NySite):
    """ """

    meta_type = METATYPE_CHMSITE
    icon = 'misc_/CHM2/Site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        self.predefined_latest_uploads = []
        self.show_releasedate = 1
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        NySite.__dict__['loadDefaultData'](self)
        self.loadSkeleton(join(CHM2_PRODUCT_PATH, 'skel'))
        manage_addNyPhotoFolder(self, ID_PHOTOARCHIVE, TITLE_PHOTOARCHIVE)
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
        #create helpdesk instance
        manage_addHelpDesk(self, ID_HELPDESKAGENT, TITLE_HELPDESKAGENT, self.getAuthenticationToolPath(1))
        #create and fill glossaries
        manage_addGlossaryCentre(self, ID_GLOSSARY_KEYWORDS, TITLE_GLOSSARY_KEYWORDS)
        self._getOb(ID_GLOSSARY_KEYWORDS).xliff_import(self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'glossary_keywords.xml')))
        manage_addGlossaryCentre(self, ID_GLOSSARY_COVERAGE, TITLE_GLOSSARY_COVERAGE)
        self._getOb(ID_GLOSSARY_COVERAGE).xliff_import(self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'glossary_coverage.xml')))
        #set glossary for pick lists
        self.keywords_glossary = ID_GLOSSARY_KEYWORDS
        self.coverage_glossary = ID_GLOSSARY_COVERAGE
        self._p_changed = 1
        #add EC CHM to network portals list
        self.admin_addnetworkportal('EC CHM', 'http://biodiversity-chm.eea.eu.int/')

    #objects getters
    def getLinkChecker(self): return self._getOb(ID_LINKCHECKER, None)
    def getLinkCheckerLastLog(self):
        entries = self.utSortObjsListByAttr(self._getOb(ID_LINKCHECKER).objectValues('LogEntry'), 'date_create', p_desc=1)
        if len(entries) > 0: return entries[0]
        else: return None
    def getPhotoArchive(self): return self._getOb(ID_PHOTOARCHIVE, None)
    def getHelpDeskAgent(self): return self._getOb(ID_HELPDESKAGENT, None)
    def getNewsArchive(self): return self._getOb('news', None)
    def getEventsArchive(self): return self._getOb('events', None)

    def get_containers_metatypes(self):
        #this method is used to display local roles, called from getUserRoles methods
        return [METATYPE_FOLDER, 'Folder', METATYPE_NYPHOTOFOLDER]

    def get_naaya_containers_metatypes(self):
        #this method is used to display local roles, called from getUserRoles methods
        return [METATYPE_FOLDER, METATYPE_NYPHOTOFOLDER]

    #layer over the Localizer and MessageCatalog
    #the scope is to centralize the list of available languages
    def gl_add_site_language_custom(self, language):
        #this is called to handle other types of multilanguage objects
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            try: r.add_language(language)
            except: pass
        for gloss in self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            try:
                catalog_obj = gloss._getOb(NAAYAGLOSSARY_CATALOG_NAME)
                index_extra = record()
                index_extra.default_encoding = 'utf-8'
                try:    catalog_obj.manage_addIndex(self.gl_get_language_name(language), 'TextIndexNG2',index_extra)
                except:    pass
                gloss.set_languages_list(language, self.gl_get_language_name(language))
                gloss._p_changed = 1
            except: pass

    def gl_del_site_languages_custom(self, languages):
        #this is called to handle other types of multilanguage objects
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            for language in languages:
                try: r.del_language(language)
                except: pass
        for gloss in self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            for language in languages:
                try: 
                    gloss.del_language_from_list(language)
                    gloss._p_changed = 1
                except: pass

    def gl_change_site_defaultlang_custom(self, language):
        #this is called to handle other types of multilanguage objects
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            try: r.manage_changeDefaultLang(language)
            except: pass

    #api
    def getOnFrontPhotos(self):
        #returns a list with the photos marked as on front
        r = [x for x in self.getPhotoArchive().getObjects() if x.approved==1 and x.topitem==1 and x.submitted==1]
        r.sort(lambda x,y: cmp(y.releasedate, x.releasedate) or cmp(x.sortorder, y.sortorder))
        return r

    def getUrlMap(self, sort='title'):
        #process and returns a map with all approved urls in the portal by domain
        #this requires NyURL pluggable content type to be present
        urls = self.query_objects_ex(meta_type=METATYPE_NYURL, approved=1)
        other_urls = self.query_objects_ex(meta_type=self.get_content_urls().keys(), approved=1)
        if sort=='url':
            #sort urls
            r1 = [(x.locator, x) for x in urls]
            r1.sort()
            #sort other urls
            r2 = []
            r2a = r2.append
            for x in other_urls:
                for y in self.get_content_urls()[x.meta_type]:
                    r2a((getattr(x, y),x))
            r2.sort()
            return r1, r2
        elif sort=='title':
            #sort urls
            r1 = [(x.title_or_id(), x) for x in urls]
            r1.sort()
            r1 = [(x[1].locator, x[1]) for x in r1]
            #sort other urls
            r2 = []
            r2a = r2.append
            for x in other_urls:
                for y in self.get_content_urls()[x.meta_type]:
                    r2a((x.title_or_id(), getattr(x, y),x))
            r2.sort()
            r2 = [(x[1], x[2]) for x in r2]
            return r1, r2
        elif sort=='server':
            #sort urls
            r1 = self.__splitbyDomains([(x.locator, x) for x in urls])
            #sort other urls
            r2 = []
            r2a = r2.append
            for x in other_urls:
                for y in self.get_content_urls()[x.meta_type]:
                    r2a((getattr(x, y),x))
            r2 = self.__splitbyDomains(r2)
            return r1, r2
        else:
            return urls

    def __splitbyDomains(self, p_list):
        #given a list o tuples (url, ob) groups them by domain name
        domains = {}
        for item in p_list:
            domain = urlparse(item[0])[1]
            domain = domain.replace('www.', '')
            domain_key = domain.split('.')
            domain_key = domain_key[:-1]
            domain_key.reverse()
            domain_key = '.'.join(domain_key)
            if not domains.has_key(domain_key):
                domains[domain_key] = [domain, []]
            domains[domain_key][1].append(item)
        domains_keys = domains.keys()
        domains_keys.sort()
        return domains_keys, domains

    def getURLProperties(self):
        #process the list of all approved items which have URL properties, by location
        #this requires NyURL pluggable content type to be present
        url_struct = {}
        #list urls
        for x in self.query_objects_ex(meta_type=METATYPE_NYURL):
            p_value = x.locator
            if isinstance(p_value, unicode): p_value = p_value.encode('utf-8')
            if p_value != '':
                if url_struct.has_key(p_value):
                    url_struct[p_value].append((x, x.getParentNode()))
                else:
                    url_struct[p_value] = [(x, x.getParentNode())]
        #list other
        for x in self.query_objects_ex(meta_type=self.get_content_urls().keys()):
            for y in self.get_content_urls()[x.meta_type]:
                p_value = getattr(x, y)
                if isinstance(p_value, unicode): p_value = p_value.encode('utf-8')
                if p_value != '':
                    if url_struct.has_key(p_value):
                        url_struct[p_value].append((x, x.getParentNode()))
                    else:
                        url_struct[p_value] = [(x, x.getParentNode())]
        return url_struct

    def setPredefinedUploads(self, predefined=[], REQUEST=None):
        """ update the predefined list of uploads """
        urls = self.utConvertToList(predefined)
        self.predefined_latest_uploads = urls
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/admin_predefined_html' % self.absolute_url())

    def getPredefinedUploads(self):
        """ get the predefined list of uploads """
        buf = []
        ba = buf.append
        t = copy(self.predefined_latest_uploads)
        for url in t:
            obj = self.unrestrictedTraverse(url, None)
            if obj is None:
                self.predefined_latest_uploads.remove(url)
            else:
                ba(obj)
        self._p_changed = 1
        return buf

    def list_glossaries(self):
        #return all the glossaries in this portal
        return self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE)

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

    security.declareProtected(view, 'getArchiveListing')
    def getArchiveListing(self, p_archive):
        """ """
        p_objects = p_archive.getObjects()
        p_objects.sort(lambda x,y: cmp(y.releasedate, x.releasedate) \
            or cmp(x.sortorder, y.sortorder))
        return self.get_archive_listing(p_objects)

    security.declareProtected(view, 'processCreateAccountForm')
    def processCreateAccountForm(self, username='', password='', confirm='', firstname='', lastname='', email='', REQUEST=None):
        """ Creates an account on the local acl_users and sends an email to the maintainer 
            with the account infomation
        """
        #create an account without any role
        try:
            self.getAuthenticationTool().manage_addUser(username, password, confirm, [], [], firstname,
                lastname, email)
        except Exception, error:
            err = error
        else:
            err = ''
        if err:
            if REQUEST:
                self.setSessionErrors(err)
                self.setCreateAccountSession(username, firstname, lastname, email, password)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        if not err:
            self.sendCreateAccountEmail(firstname + ' ' + lastname, email, username, REQUEST)
        if REQUEST:
            self.setSession('title', 'Thank you for registering')
            self.setSession('body', 'You will receive a confirmation email.')
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    def sendCreateAccountEmail(self, p_name, p_email, p_username, REQUEST):
        #sends a confirmation email to the newlly created account's owner
        email_template = self.getEmailTool()._getOb('email_createaccount')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@EMAIL@@', p_email)
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        mail_from = self.mail_address_from
        self.getEmailTool().sendEmail(l_content, p_email, mail_from, l_subject)


    security.declareProtected(view_management_screens, 'duplicate_translate')
    def duplicate_translate(self, property, source_lang, target_lang):
        """
        Duplicates translate in one language.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            v = x.getLocalProperty(property, target_lang)
            if len(v) <= 0 :
                x._setLocalPropValue(property, target_lang, x.getLocalProperty(property, source_lang))
                x._p_changed = 1
                self.recatalogNyObject(x)
        return "done"

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_urls_html')
    def admin_urls_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_urls')

    security.declareProtected(PERMISSION_ADMINISTRATE, 'admin_submissions_html')
    def admin_submissions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_submissions')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'admin_deletions_html')
    def admin_deletions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_deletions')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_urls_html')
    def admin_urls_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_urls')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_comments_html')
    def admin_comments_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_comments')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_predefined_html')
    def admin_predefined_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_predefined')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkchecker_html')
    def admin_linkchecker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkchecker')

    #site pages
    security.declareProtected(view, 'urlmap_html')
    def urlmap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_urlmap')

InitializeClass(CHMSite)
