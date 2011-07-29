import os
from os.path import join
from urlparse import urlparse
from copy import copy
from cStringIO import StringIO
from zipfile import ZipFile
from PIL import Image
import urllib

from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from ZPublisher.HTTPRequest import record
from App.ImageFile import ImageFile
from OFS.Image import manage_addImage
from OFS.Folder import manage_addFolder

from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker
from Products.NaayaPhotoArchive.NyPhotoFolder import addNyPhotoFolder
from Products.NaayaPhotoArchive.constants import *
from Products.NaayaNetRepository.constants import *
from Products.NaayaHelpDeskAgent.HelpDesk import manage_addHelpDesk
from Products.NaayaGlossary.constants import *
from Products.NaayaCalendar.EventCalendar import manage_addEventCalendar
from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
from Products.NaayaForum.NyForum import addNyForum
from Products.CHM2.managers.captcha_tool import captcha_tool
from Products.NaayaCore.managers.utils import make_id

METATYPE_NYURL = 'Naaya URL'

class Extra_for_DateRangeIndex:
    """hack for a bug in DateRangeIndex ---'dict' object has no attribute 'since_field' """
    def __init__(self, **kw):
        for key in kw.keys():
            setattr(self, key, kw[key])

manage_addCHMSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addCHMSite(self, id='', title='', lang=None, google_api_keys=None,
                      load_glossaries=[], REQUEST=None):
    """ """
    if REQUEST is not None:
        # we'll need the SESSION later on; grab it early so we don't
        # get a ConflictError.
        REQUEST.SESSION
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    self._setObject(id, CHMSite(id, title=title, lang=lang))
    chm_site = self._getOb(id)
    chm_site.loadDefaultData(load_glossaries)

    if google_api_keys:
        engine = chm_site.getGeoMapTool()['engine_google']
        engine.api_keys = google_api_keys

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class CHMSite(NySite):
    """ """

    meta_type = METATYPE_CHMSITE
    icon = 'misc_/CHM2/Site.gif'

    manage_options = (
        NySite.manage_options
    )
    product_paths = NySite.product_paths + [CHM2_PRODUCT_PATH]

    security = ClassSecurityInfo()
    default_geographical_coverage = ''

    def __init__(self, *args, **kwargs):
        """ """
        self.predefined_latest_uploads = []
        self.show_releasedate = 1
        self.workgroups = []
        NySite.__dict__['__init__'](self, *args, **kwargs)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, load_glossaries=[]):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #load site skeleton - configuration
        self.loadSkeleton(CHM2_PRODUCT_PATH)

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')

        #set default PhotoFolder
        addNyPhotoFolder(self, id=ID_PHOTOARCHIVE, title=TITLE_PHOTOARCHIVE)
        self._getOb(ID_PHOTOARCHIVE).approveThis()

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

        #set default main topics
        self.getPropertiesTool().manageMainTopics(['convention', 'cooperation', 'network', 'information'])

        #create helpdesk instance
        manage_addHelpDesk(self, ID_HELPDESKAGENT, TITLE_HELPDESKAGENT, self.getAuthenticationToolPath(1))
        #create NaayaCalendar instance
        manage_addEventCalendar(self, id="portal_calendar", title='Calendar of Events', description='',
                            day_len='2', start_day='Monday', catalog=self.getCatalogTool().id, REQUEST=None)
        calendar = self._getOb('portal_calendar')
        calendar.cal_meta_types = calendar.setCalMetaTypes('Naaya Event')
        #create index for Naaya Calendar
        extra=Extra_for_DateRangeIndex(since_field='start_date', until_field='end_date')
        self.getCatalogTool().manage_addIndex("resource_interval", 'DateRangeIndex', extra=extra)

        #create and fill glossaries
        if 'coverage' in load_glossaries:
            self.add_glossary_coverage()
        if 'keywords' in load_glossaries:
            self.add_glossary_keywords()
        if 'chm_terms' in load_glossaries:
            self.add_chm_terms_glossary()

        #set glossary for pick lists
        self._p_changed = 1
        #add Forum instance
        addNyForum(self, id='portal_forum', title='CHM Forum', description='', categories=['CHM', 'Biodiversity', 'Other'], file_max_size=0, REQUEST=None)
        #add EC CHM to network portals list
        self.admin_addnetworkportal('EC CHM', 'http://biodiversity-chm.eea.europa.eu/')

    def get_data_path(self):
        """ """
        return CHM2_PRODUCT_PATH

    security.declareProtected(view_management_screens, 'add_glossary_coverage')
    def add_glossary_coverage(self):
        manage_addGlossaryCentre(self, ID_GLOSSARY_COVERAGE, TITLE_GLOSSARY_COVERAGE)
        glossary = self._getOb(ID_GLOSSARY_COVERAGE)
        glossary_languages = [
                ('Arabic', 'ar'), ('Bulgarian', 'bg'), ('Catalan', 'ca'),
                ('Czech', 'cs'), ('Danish', 'da'), ('German', 'de'),
                ('Greek', 'el'), ('English', 'en'), ('Esperanto', 'eo'),
                ('Spanish', 'es'), ('Estonian', 'et'), ('Basque', 'eu'),
                ('Finnish', 'fi'), ('Faeroese', 'fo'), ('French', 'fr'),
                ('Irish', 'ga'), ('Croatian', 'hr'), ('Hungarian', 'hu'),
                ('Armenian', 'hy'), ('Islandic', 'is'), ('Italian', 'it'),
                ('Lithuanian', 'lt'), ('Latvian', 'lv'), ('Macedonian', 'mk'),
                ('Maltese', 'mt'), ('Dutch', 'nl'), ('Polish', 'pl'),
                ('Portuguese', 'pt'), ('Romanian', 'ro'), ('Russian', 'ru'),
                ('Slovak', 'sk'), ('Slovenian', 'sl'), ('Albanian', 'sq'),
                ('Serbian', 'sr'), ('Swedish', 'sv'), ('Turkish', 'tr'),
                ('Ukrainian', 'uk'),
            ]
        for name, code in glossary_languages:
            glossary.addLanguage(name, code)
        import_files = os.listdir(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'coverage_glossary_translations'))
        import_files.sort()
        for file in [file for file in import_files if file.endswith('.xml')]:
            glossary.xliff_import(self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'coverage_glossary_translations', file)))

        self.coverage_glossary = ID_GLOSSARY_COVERAGE
        schema_tool = self.portal_schemas
        coverage = schema_tool.NyDocument['coverage-property']
        coverage.saveProperties(glossary_id=self.coverage_glossary, all_content_types=True, sortorder=coverage.sortorder, title=coverage.title, visible=coverage.visible)

    security.declareProtected(view_management_screens, 'add_glossary_keywords')
    def add_glossary_keywords(self):
        manage_addGlossaryCentre(self, ID_GLOSSARY_KEYWORDS, TITLE_GLOSSARY_KEYWORDS) 
        self._getOb(ID_GLOSSARY_KEYWORDS).xliff_import(self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'glossary_keywords.xml'))) 
        self.keywords_glossary = ID_GLOSSARY_KEYWORDS
        schema_tool = self.portal_schemas
        keywords = schema_tool.NyDocument['keywords-property']
        keywords.saveProperties(glossary_id=self.keywords_glossary, all_content_types=True, sortorder=keywords.sortorder, title=keywords.title, visible=keywords.visible)

    security.declareProtected(view_management_screens, 'add_chm_terms_glossary')
    def add_chm_terms_glossary(self, set_up_sync=True):
        manage_addGlossaryCentre(self, ID_CHM_TERMS, TITLE_CHM_TERMS)
        glossary = self._getOb(ID_CHM_TERMS)

        skel_dump_path = os.path.join(CHM2_PRODUCT_PATH, 'skel', 'others',
                                      'chm_terms_translations')
        dump_data = glossary_dump_from_skel(skel_dump_path)
        glossary.dump_import(dump_data)

        if set_up_sync:
            glossary.sync_remote_url = CHM_TERMS_MASTER_URL


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

    #workgroups API
    def getWorkgroupsList(self):
        """
        Returns the list of worgroups as a list of tuples
        where a tuple identifies a workgroup.
        """
        return self.workgroups

    def displayWorkgroupsList(self, skey='', rkey=''):
        """
        Returns the list of workgroups as a sorted list
        of tuples where a tuple identifies a workgroup.
        """
        r = self.workgroups
        if skey in ['title', 'role', 'location']:
            if skey == 'title': t = [(x[1], x) for x in r]
            elif skey == 'location': t = [(x[2], x) for x in r]
            elif skey == 'role': t = [(x[3], x) for x in r]
            t.sort()
            if rkey: t.reverse()
            r = [x[1] for x in t]
        return r

    def getWorkgroupById(self, id):
        """
        Returns the workgroup with the given id.
        If no workgroup exists then B{None} is returned.
        """
        for x in self.workgroups:
            if x[0]==id: return x
        return None

    def getWorkgroupByLocation(self, loc):
        """ """
        for x in self.workgroups:
            if x[2]==loc: return x
        return None

    def getWorkgoupsLocations(self):
        """ """
        return [x[2] for x in self.workgroups]

    def sortUsersList(self, l, skey='', rkey=''):
        """
        Given a list a tuples where a tuple contains info
        about an user (name, fullname, email, roles)
        returns the list sorted.
        """
        r = copy(l)
        if skey in ['username', 'name', 'email']:
            if skey == 'username': t = [(x['username'], x) for x in r]
            elif skey == 'name': t = [(x['name'], x) for x in r]
            elif skey == 'email': t = [(x['email'], x) for x in r]
            t.sort()
            if rkey: t.reverse()
            r = [x[1] for x in t]
        return r

    def getAssignedUsers(self):
        """
        Returns the list of users that do not belong to any group, but
        they have some permissions in the portal.
        """
        meta_types = self.get_containers_metatypes()
        #from Root
        auth_tool = self.getAuthenticationTool()
        users_roles = {}
        for username in auth_tool.user_names():
            user = auth_tool.getUser(username)
            roles = auth_tool.getUserRoles(user)
            for role in roles:
                if not users_roles.has_key(username): users_roles[username] = {'username': username, 'name': '%s %s' % (user.firstname, user.lastname), 'email': user.email, 'roles': []}
                users_roles[username]['roles'].append((role, '/'))
        #from site
        for folder in self.getCatalogedObjects(meta_type=meta_types, has_local_role=1):
            for roles_tuple in folder.get_local_roles():
                local_roles = auth_tool.getLocalRoles(roles_tuple[1])
                if roles_tuple[0] in auth_tool.user_names() and len(local_roles) > 0:
                    for role in local_roles:
                        username = str(roles_tuple[0])
                        if not users_roles.has_key(username):
                            user = auth_tool.getUser(username)
                            users_roles[username] = {'username': username, 'name': '%s %s' % (user.firstname, user.lastname), 'email': user.email, 'roles': []}
                        users_roles[username]['roles'].append((role, folder.absolute_url(1)))
        return users_roles.values()

    def getUserAllRoles(self, name):
        """
        Returns a list with all user roles (including local in all portal).
        """
        for x in self.getAssignedUsers():
            if x['username'] == name: return x['roles']
        return []

    def getUnassignedUsers(self):
        """
        Returns the list of users that do not belong to any group and
        don't have any permissions at all in the portal.
        """
        auth_tool = self.getAuthenticationTool()
        r = []
        for x in self.utListDifference(auth_tool.user_names(), [x['username'] for x in self.getAssignedUsers()]):
            user = auth_tool.getUser(x)
            r.append({'username': x, 'name': '%s %s' % (user.firstname, user.lastname), 'email': user.email, 'roles': []})
        return r

    def getWorkgroupUsers(self, id, skey='username', rkey='0'):
        """ """
        wg = self.getWorkgroupById(id)
        if wg:
            r = []
            loc = self.unrestrictedTraverse(wg[2])
            #remove local roles
            for x in loc.get_local_roles():
                roles = list(x[1])
                if 'Owner' in x[1]: roles.remove('Owner')
                if roles: r.append((x[0], roles))
            r.sort()
            if rkey=='1': r.reverse()
            return r
        return []

    def isUserInWorkgroup(self, id, name):
        """
        Test if the given user is part of the workgroup
        with the specified id.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            r = []
            loc = self.unrestrictedTraverse(wg[2])
            for x in loc.get_local_roles():
                roles = list(x[1])
                if 'Owner' in x[1]: roles.remove('Owner')
                if roles and x[0]==name: return 1
        return 0

    def getUsersWorkgroups(self, name):
        """
        Returns a list with all workgroups that the
        user is part of.
        """
        l = []
        for wg in self.workgroups:
            r = []
            loc = self.unrestrictedTraverse(wg[2])
            for x in loc.get_local_roles():
                roles = list(x[1])
                if 'Owner' in x[1]: roles.remove('Owner')
                if roles and x[0]==name: l.append(wg)
        return l

    def getNonWorkgroupUsers(self, id):
        """ """
        auth_tool = self.getAuthenticationTool()

        all_uids = auth_tool.user_names()
        wg_uids = [x[0] for x in self.getWorkgroupUsers(id)]
        nonwg_uids = self.utListDifference(all_uids, wg_uids)

        local_user_info = auth_tool.get_local_usernames()
        return [info for info in local_user_info if info['uid'] in nonwg_uids]

    def add_userto_workgroup(self, loc, name, roles):
        """ """
        loc.manage_setLocalRoles(name, roles)

    def del_userfrom_workgroup(self, loc, name):
        """ """
        loc.manage_delLocalRoles([name])

    def groupByLocation(self, roles):
        """ """
        d = {}
        for role in roles:
            if not d.has_key(role[1]): d[role[1]] = []
            d[role[1]].append(role[0])
        return d.items()

    #layer over the Localizer and MessageCatalog
    #the scope is to centralize the list of available languages
    def gl_add_site_language_custom(self, language):
        #this is called to handle other types of multilanguage objects
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains(meta_type=[METATYPE_NYPHOTOFOLDER, METATYPE_NYPHOTO]):
            x = catalog_tool.getobject(b.data_record_id_)
            try: x.add_language(language)
            except: pass
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            try: r.add_language(language)
            except: pass
        for gloss in self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            try:
                language_name = self.gl_get_language_name(language)
                catalog_obj = gloss.getGlossaryCatalog()
                index_extra = record()
                index_extra.default_encoding = 'utf-8'
                try:    catalog_obj.manage_addIndex(language_name, 'TextIndexNG2',index_extra)
                except:    pass
                gloss.set_languages_list(language, language_name)
                gloss.updateObjectsByLang(language_name)
                gloss._p_changed = 1
            except:
                pass

    def gl_del_site_languages_custom(self, languages):
        #this is called to handle other types of multilanguage objects
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains(meta_type=[METATYPE_NYPHOTOFOLDER, METATYPE_NYPHOTO]):
            x = catalog_tool.getobject(b.data_record_id_)
            for language in languages:
                try: x.del_language(language)
                except: pass
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
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains(meta_type=[METATYPE_NYPHOTOFOLDER, METATYPE_NYPHOTO]):
            x = catalog_tool.getobject(b.data_record_id_)
            try: x.manage_changeDefaultLang(language)
            except: pass
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            try: r.manage_changeDefaultLang(language)
            except: pass

    #api
    def getOnFrontPhotos(self):
        #returns a list with the photos marked as on front
        r = [x for x in self.getPhotoArchive().getObjects() if x.approved==1 and getattr(x, 'topitem', 0) and x.submitted==1]
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
            if obj: ba(obj)
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
    def getArchiveListing(self, p_archive, p_attr='releasedate', p_desc=1):
        """ """
        p_objects = p_archive.getObjects()
        p_objects = self.utSortObjsListByAttr(p_objects, p_attr, p_desc)
        return self.get_archive_listing(p_objects)

    security.declareProtected(view, 'processCreateAccountForm')
    def processCreateAccountForm(self, username='', password='', confirm='', firstname='', lastname='', email='', REQUEST=None):
        """ Creates an account on the local acl_users and sends an email to the maintainer
            with the account infomation
        """
        #create an account without any role
        try:
            self.getAuthenticationTool().manage_addUser(username, password, confirm, [], [], firstname, lastname, email, 0)
        except Exception, error:
            err = error
        else:
            err = ''
        if err:
            if REQUEST:
                self.setSessionErrorsTrans(str(err))
                self.setCreateAccountSession(username, firstname, lastname, email, password)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        if not err:
            self.sendCreateAccountEmail('', firstname + ' ' + lastname, email, '', username, '', '', '')
        if REQUEST:
            self.setSession('title', 'Thank you for registering')
            self.setSession('body', 'You will receive a confirmation email.')
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    def sendCreateAccountEmail(self, p_to, p_name, p_email, p_organisation, p_username, p_location_path, p_location_title, p_comments, **kwargs):
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

    security.declareProtected(view, 'getRequestParams')
    def getRequestParams(self, REQUEST=None):
        """returns a REQUEST.QUERY_STRING (using REQUEST.form,
            REQUEST.form=REQUEST.QUERY_STRING as a dictionary)"""
        ignore_list = ['skey', 'rkey']
        res=''
        if REQUEST:
            for key in self.REQUEST.form.keys():
                if key not in ignore_list:
                    res=res+key+'='+str(self.REQUEST.form[key])+'&'
        return res

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addworkgroup')
    def admin_addworkgroup(self, title='', location='', role='', REQUEST=None):
        """ """
        err = []
        if title=='':
            err.append('Workgroup name is required')
        if location=='':
            err.append('Location is required')
        else:
            try:
                #check for a valid location
                ob = self.unrestrictedTraverse(location)
            except:
                err.append('Invalid location')
            else:
                #check if no group was defiend for this location
                if self.getWorkgroupByLocation(location):
                    err.append(
                        'A workgroup is already defined for this location')
        if role=='':
            err.append('Role is required')
        if err:
            if REQUEST is not None:
                self.setSessionErrorsTrans(err)
                self.setSession('title', title)
                self.setSession('location', location)
                self.setSession('role', role)
                return REQUEST.RESPONSE.redirect('%s/admin_addworkgroup_html' %
                                                 self.absolute_url())
        else:
            id = self.utGenRandomId(4)
            self.workgroups.append((id, title, location, role))
            self._p_changed = True
            if REQUEST is not None:
                self.setSessionInfoTrans("Workgroup added")
                REQUEST.RESPONSE.redirect('%s/admin_workgroups_html?w=%s' %
                                                 (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_delworkgroup')
    def admin_delworkgroup(self, ids=[], REQUEST=None):
        """
        Delete workgroup(s).
        """
        redirect_url = REQUEST.environ.get('HTTP_REFERER',
                            '%s/admin_workgroups_html' % self.absolute_url())
        if len(ids) == 0:
            if REQUEST is not None:
                self.setSessionErrorsTrans("No workgroup(s) selected")
                return REQUEST.RESPONSE.redirect(redirect_url)
            else:
                raise ValueError("No workgroup(s) provided")
        for id in self.utConvertToList(ids):
            wg = self.getWorkgroupById(id)
            if wg:
                loc = self.unrestrictedTraverse(wg[2])
                #remove local roles
                for x in loc.get_local_roles():
                    isowner = 0
                    if 'Owner' in x[1]: isowner = 1
                    self.del_userfrom_workgroup(loc, x[0])
                    if isowner: self.add_userto_workgroup(loc, x[0], ['Owner'])
                #remove workgroup
                self.workgroups.remove(wg)
                self._p_changed = 1
        if REQUEST is not None:
            self.setSessionInfoTrans("Workgroup(s) deleted")
            return REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_userworkgroups')
    def admin_userworkgroups(self, name='', ids=[], REQUEST=None):
        """
        (Un)Assign an user from/to one or more workgroups.
        """
        ids = self.utConvertToList(ids)
        user_wgs = [x[0] for x in self.getUsersWorkgroups(name)]
        #add to new workgroups
        for id in self.utListDifference(ids, user_wgs):
            self.admin_addusertoworkgroup(id, name)
        #remove from workgroups
        for id in self.utListDifference(user_wgs, ids):
            self.admin_delusersfromworkgroup(id, [name])
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect('%s/admin_userroles_html?name=%s'
                                             % (self.absolute_url(), name))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addusertoworkgroup')
    def admin_addusertoworkgroup(self, id='', name='', REQUEST=None):
        """
        Assign an user to an workgroup.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            loc = self.unrestrictedTraverse(wg[2])
            self.add_userto_workgroup(loc, name, [wg[3]])
        if REQUEST:
            self.setSessionInfoTrans("User ${name} assigned to workgroup",
                                     name=name)
            return REQUEST.RESPONSE.redirect('%s/admin_workgroup_html?w=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduserstoworkgroup')
    def admin_adduserstoworkgroup(self, id='', names=[], REQUEST=None):
        """
        Assign one or more users to a workgroup.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            loc = self.unrestrictedTraverse(wg[2])
            for name in self.utConvertToList(names):
                self.add_userto_workgroup(loc, name, [wg[3]])
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect('%s/admin_users_unnassigned' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_delusersfromworkgroup')
    def admin_delusersfromworkgroup(self, id='', names=[], REQUEST=None):
        """
        Unassign one or more users from a workgroup.
        """
        if REQUEST is not None:
            redirect_url = REQUEST.get('HTTP_REFERER',
                                           '%s/admin_workgroup_html?w=%s' %
                                            (self.absolute_url(), id))
        if len(names) == 0:
            if REQUEST is not None:
                self.setSessionErrorsTrans("No user(s) selected")
                return REQUEST.RESPONSE.redirect(redirect_url)
            else:
                raise ValueError("No user(s) provided")

        wg = self.getWorkgroupById(id)
        if wg:
            loc = self.unrestrictedTraverse(wg[2])
            for x in loc.get_local_roles():
                if x[0] in self.utConvertToList(names):
                    isowner = 0
                    if 'Owner' in x[1]: isowner = 1
                    self.del_userfrom_workgroup(loc, x[0])
                    if isowner: self.add_userto_workgroup(loc, x[0], ['Owner'])
        if REQUEST:
            self.setSessionInfoTrans("User(s) deleted from workgroup")
            return REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_revokeuserroles')
    def admin_revokeuserroles(self, name='', roles=[], REQUEST=None):
        """
        Revoke roles from an user.
        """
        redirect_url = REQUEST.environ.get('HTTP_REFERER',
                                           '%s/admin_userroles_html?name=%s'
                                             % (self.absolute_url(), name))
        if len(roles) == 0:
            if REQUEST is not None:
                self.setSessionErrorsTrans("No role(s) selected")
                return REQUEST.RESPONSE.redirect(redirect_url)
            else:
                raise ValueError("No role(s) provided")

        auth_tool = self.getAuthenticationTool()

        for location in self.utConvertToList(roles):
            auth_tool.manage_revokeUserRole(name, location, REQUEST)

        if REQUEST is not None:
            self.setSessionInfoTrans("Role(s) revoked")
            return REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(view, 'getCaptcha')
    def getCaptcha(self):
        """ generate a Captcha image """
        g = captcha_tool()
        g.defaultSize = (100, 20)
        i = g.render()
        newimg = StringIO()
        i.save(newimg, "JPEG")
        newimg.seek(0)
        #set the word on session
        self.setSession('captcha', g.solutions[0])
        return newimg.getvalue()

    #overwrite the Naaaya processFeedbackForm function. CAPTCHA added
    security.declareProtected(view, 'processFeedbackForm')
    def processFeedbackForm(self, username='', email='', comments='', contact_word='', REQUEST=None):
        """ """
        err = []
        if contact_word=='' or contact_word!=self.getSession('captcha', None):
            err.append('The word you typed does not match with the one shown in the image. Please try again.')
        if username.strip() == '':
            err.append('The full name is required')
        if email.strip() == '':
            err.append('The email is required')
        if comments.strip() == '':
            err.append('The comments are required')
        if err:
            if REQUEST:
                self.setSessionErrorsTrans(err)
                self.setFeedbackSession(username, email, comments)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        else:
            self.sendFeedbackEmail(self.administrator_email, username, email, comments)
            if REQUEST:
                self.setSession('title', 'Thank you for your feedback')
                self.setSession('body', 'The administrator will process your comments and get back to you.')
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_usersassigned_html')
    def admin_usersassigned_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users_assigned')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_usersunnassigned_html')
    def admin_usersunnassigned_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users_unnassigned')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS,
                              'admin_userroles_html')
    def admin_userroles_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                    'site_admin_userroles')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addworkgroup_html')
    def admin_addworkgroup_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_addworkgroup')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_workgroups_html')
    def admin_workgroups_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_workgroups')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_workgroup_html')
    def admin_workgroup_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_workgroup')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkchecker_html')
    def admin_linkchecker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkchecker')

    #site pages
    security.declareProtected(view, 'urlmap_html')
    def urlmap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_urlmap')

    #update scripts
    security.declareProtected(view_management_screens, 'fix_selection_lists')
    def fix_selection_lists(self, REQUEST=None):
        """ """
        from Products.Naaya.managers.skel_parser import skel_parser
        #remove absolete eventtypes property
        try:
            delattr(self, '_events_tool__eventtypes')
            self._p_changed = 1
        except:
            pass
        #reload Naaya Event pluggable type
        self.manage_uninstall_pluggableitem(meta_type=METATYPE_NYEVENT)
        self.manage_install_pluggableitem(meta_type=METATYPE_NYEVENT)
        #reload administration portlet
        self.getPortletsTool()._getOb('portlet_administration').pt_edit(text=self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'portlets', 'portlet_administration.zpt'), 'r'), content_type='')
        #load data
        for x in [NAAYA_PRODUCT_PATH, CHM2_PRODUCT_PATH]:
            skel_handler, error = skel_parser().parse(self.futRead(join(x, 'skel', 'skel.xml'), 'r'))
            if skel_handler is not None:
                formstool_ob = self.getFormsTool()
                portletstool_ob = self.getPortletsTool()
                if skel_handler.root.forms is not None:
                    for form in skel_handler.root.forms.forms:
                        content = self.futRead(join(x, 'skel', 'forms', '%s.zpt' % form.id), 'r')
                        form_ob = formstool_ob._getOb(form.id, None)
                        if form_ob is None:
                            formstool_ob.manage_addTemplate(id=form.id, title=form.title, file='')
                            form_ob = formstool_ob._getOb(form.id, None)
                        form_ob.pt_edit(text=content, content_type='')
                if skel_handler.root.portlets is not None:
                    for reflist in skel_handler.root.portlets.reflists:
                        reflist_ob = portletstool_ob._getOb(reflist.id, None)
                        if reflist_ob is None:
                            portletstool_ob.manage_addRefTree(reflist.id, reflist.title, reflist.description)
                            reflist_ob = portletstool_ob._getOb(reflist.id)
                        else:
                            reflist_ob.manage_delObjects(reflist_ob.objectIds())
                        for item in reflist.items:
                            reflist_ob.manage_addRefTreeNode(item.id, item.title)
        return 'Script OK.'

    security.declareProtected(view, 'links_group_html')
    def links_group_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_links_group')

    security.declareProtected(view_management_screens, 'dumpFormsLayout')
    def dumpFormsLayout(self):
        """ """
        path = join(CLIENT_HOME, self.id)
        path_forms = join(path, 'forms')
        if not os.path.isdir(path):
            try: os.mkdir(path)
            except: raise OSError, 'Can\'t create directory %s' % path
        if not os.path.isdir(path_forms):
            try: os.mkdir(path_forms)
            except: raise OSError, 'Can\'t create directory %s' % path_forms
        for x in self.getFormsTool().objectValues():
            file = open(join(path_forms, '%s.zpt' % x.id), 'w')
            file.write(x.document_src())
            file.close()
        return 'DUMP OK.'


    #expandable portlets functions
    security.declareProtected(view, 'epFromCookiesToSession')
    def epFromCookiesToSession(self):
        """
        Moves the data from cookies to session for expandable portlets.
        """
        temp = ''
        c = self.REQUEST.cookies
        s = self.getSession('ep_expanded_portlets', {})
        #transfer the cookies to session
        if c.has_key('ep_expanded_portlets'):
            for i in c['ep_expanded_portlets'].split('*'):
                x = i.split('|')
                path = x[0]
                portlet = x[1]
                value = x[2]
                if value == '1':
                    try:
                        s[portlet].pop(path)
                    except:
                        pass
                if value == '2': #set portlet visible with ignorepath
                    try:
                        s[portlet] = {}
                    except:
                        pass
                if value == '-1' or value == '-2':
                    try:
                        s[portlet][path] = value
                    except:
                        s[portlet] = {}
                        s[portlet][path] = value

        self.setSession('ep_expanded_portlets', s)
        #delete the cookies
        self.REQUEST.RESPONSE.setCookie('ep_expanded_portlets','',expires='Wed, 10 Feb 1970 10:00:00 GMT',path="/")
        return temp

    def epIsPortletCollapsed(self, path='', portlet='', ignorepath = False):
        if ignorepath:
            try:
                if len(self.getSession('ep_expanded_portlets', {})[portlet]) == 0:
                    return False
                else:
                    return True
            except:
                return False
        else:
            try:
                dummy = self.getSession('ep_expanded_portlets', {})[portlet][path]
                return True
            except:
                return False

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_properties')
    def admin_properties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST is not None:
            kwargs.update(REQUEST.form)
        self.default_geographical_coverage = kwargs.get('default_geographical_coverage', False)
        super(CHMSite, self).admin_properties(REQUEST=REQUEST, **kwargs)

    chm_common_css = ImageFile('www/chm_common.css', globals())


    security.declareProtected(view, 'get_related_items')
    def get_related_items(self, item):
        """ """
        lang = self.gl_get_selected_language()
        attr_name = 'tags_' + lang
        if not hasattr(item.aq_base, attr_name):
            return []
        keywords = getattr(item, attr_name)
        if not keywords:
            return []
        search_args = {attr_name: keywords, 'approved': 1}
        results = self.getCatalogedObjectsCheckView(**search_args)
        if item in results:
            results.remove(item)
        return results

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'upload_maintopic_temp_image')
    def upload_maintopic_temp_image(self, REQUEST):
        """ """
        temp_folder = self.getSite().temp_folder
        file = REQUEST.form.get('upload_file', None)

        image_size = get_image_size(file)
        if file is None or not image_size:
            return None
        x = image_size[0]
        y = image_size[1]
        filename = file.filename
        id = make_id(temp_folder, id=filename)
        manage_addImage(temp_folder, id, file=file)
        ob = getattr(temp_folder, id)
        ob.filename = filename
        ob.p_changed = 1
        if 4 * x > 3 * y:
            return (ob.absolute_url(), (x - 3 * y / 4) / 2, 0,   (x + 3 * y / 4) / 2, y)
        else:
            return (ob.absolute_url(), 0, (y - (4 * x / 3)) / 2,    x, (y + (4 * x / 3)) / 2)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_savemaintopic_image')
    def admin_savemaintopic_image(self, mainsection, upload_picture_url,
            x1, y1, x2, y2, REQUEST=None):
        """ """
        def process_picture(picture, crop_coordinates):
            image_string = data2stringIO(picture.data)
            img = Image.open(image_string)
            fmt = img.format
            crop_size = crop_coordinates[2] - crop_coordinates[0]
            if crop_size == 0:
                x = img.size[0]
                y = img.size[1]
                crop_size = x
                if 4 * x > 3 * y:
                    crop_coordinates = ((x - 3 * y / 4) / 2, 0, (x + 3 * y / 4) / 2, y)
                else:
                    crop_coordinates = (0, (y - (4 * x / 3)) / 2, x, (y + (4 * x / 3)) / 2)

            img = img.crop(crop_coordinates)
            if crop_size > 162:
                crop_size = 162
            try:
                img = img.resize((crop_size, 4 * crop_size / 3), Image.ANTIALIAS)
            except AttributeError:
                img = img.resize((width, height))
            newimg = StringIO()
            img.save(newimg, fmt, quality=85)
            return newimg.getvalue()

        layout_tool = self.getLayoutTool()
        # not using get_current_skin to make it work for CHMBE
        skin = layout_tool._getOb(layout_tool.getCurrentSkinId()) # to work for CHMBE
        # add images folder if it doesn't exist
        if not skin.hasObject('main_section_images'):
            manage_addFolder(skin, 'main_section_images')
        main_section_images = skin._getOb('main_section_images')

        # remove old image if exists
        if main_section_images.hasObject(mainsection):
            main_section_images.manage_delObjects([mainsection])

        if upload_picture_url:
            upload_picture_url = urllib.unquote(upload_picture_url)
            temp_folder = self.getSite().temp_folder
            picture_id = upload_picture_url.split('/')[-1]
            picture = getattr(temp_folder, picture_id)
            crop_coordinates = (x1, y1, x2, y2)
            croped_picture = process_picture(picture, crop_coordinates)
            manage_addImage(main_section_images, mainsection, croped_picture)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

InitializeClass(CHMSite)


def add_terms_property_to_schema(schema):
    try:
        schema.getWidget('chm_terms')
    except KeyError:
        pass # it's missing, we add it.
    else:
        return # it's already there.

    prop_spec = {
        'sortorder': 43,
        'widget_type': 'Glossary',
        'display_mode': 'values-list',
        'label': 'CHM terms',
        'glossary_id': ID_CHM_TERMS,
        'localized': True,
    }

    if schema.getId() == 'NyMunicipality':
        return
    elif schema.getId() == 'NyExpert':
        prop_spec['sortorder'] = 215

    schema.addWidget('chm_terms', **prop_spec),

def add_terms_property_to_all_schemas(site):
    schema_tool = site.getSchemaTool()
    for schema in schema_tool.objectValues(['Naaya Schema']):
        add_terms_property_to_schema(schema)

def handle_content_type_installed(evt):
    schema_tool = evt.context.getSchemaTool()
    schema = schema_tool.getSchemaForMetatype(evt.meta_type)
    if schema is not None:
        add_terms_property_to_schema(schema)

def glossary_dump_from_skel(files_path):
    """
    Generate a Zip dump from the given folder. Returns a StringIO
    containing the Zip data.
    """

    dump_file = StringIO()
    dump_zip = ZipFile(dump_file, 'w')

    dump_zip.write(os.path.join(files_path, 'metadata.json'),
                   'glossary/metadata.json')
    dump_zip.write(os.path.join(files_path, 'translations.xml'),
                   'glossary/translations.xml')

    dump_zip.close()
    dump_file.seek(0)

    return dump_file

def update_chm_terms_glossary(glossary):
    skel_dump_path = os.path.join(CHM2_PRODUCT_PATH, 'skel', 'others',
                                  'chm_terms_translations')
    dump_data = glossary_dump_from_skel(skel_dump_path)
    glossary.dump_import(dump_data)
    import transaction; transaction.commit()

def get_image_size(file):
    """
    Test if the specified uploaded B{file} is a valid image.
    """
    try:
        image = Image.open(file)
    except: # Python Imaging Library doesn't recognize it as an image
        return False
    else:
        file.seek(0)
        return image.size

def data2stringIO(data):
    str_data = StringIO()
    if isinstance(data, str):
        str_data.write(data)
    else:
        while data is not None:
            str_data.write(data.data)
            data=data.next
    str_data.seek(0)
    return str_data
