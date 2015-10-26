import os
from os.path import join
from urlparse import urlparse
from copy import copy
from cStringIO import StringIO
from zipfile import ZipFile
from PIL import Image
import urllib

from zope.interface import implements
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from ZPublisher.HTTPRequest import record
from App.ImageFile import ImageFile
from OFS.Image import manage_addImage
from OFS.Folder import manage_addFolder
from zope.publisher.browser import BrowserPage

from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker
from Products.NaayaPhotoArchive.NyPhotoGallery import addNyPhotoGallery
from Products.NaayaPhotoArchive.constants import *
from Products.NaayaNetRepository.constants import *
from Products.NaayaGlossary.constants import *
from Products.NaayaCalendar.EventCalendar import manage_addEventCalendar
from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
from Products.NaayaForum.NyForum import addNyForum
from Products.NaayaCore.managers.utils import make_id
from naaya.component import bundles
from Products.Naaya.managers.skel_parser import skel_handler_for_path
from naaya.core.zope2util import json_response, iter_file_data

from interfaces import ICHMSite

METATYPE_NYURL = 'Naaya URL'

class Extra_for_DateRangeIndex:
    """hack for a bug in DateRangeIndex ---'dict' object has no attribute 'since_field' """
    def __init__(self, **kw):
        for key in kw.keys():
            setattr(self, key, kw[key])


def _get_skel_handler(bundle_name):
    if bundle_name == 'CHM':
        skel_path = os.path.join(CHM2_PRODUCT_PATH, 'skel')
        return skel_handler_for_path(skel_path)
    elif bundle_name == 'CHM3':
        skel_path = os.path.join(CHM2_PRODUCT_PATH, 'skel-chm3')
        return skel_handler_for_path(skel_path)
    else:
        return None


manage_addCHMSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addCHMSite(self, id='', title='', lang=None, google_api_keys=None,
                      load_glossaries=[], bundle_name='CHM', REQUEST=None):
    """ """
    if REQUEST is not None:
        # we'll need the SESSION later on; grab it early so we don't
        # get a ConflictError.
        REQUEST.SESSION
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    chm_site = CHMSite(id, title=title, lang=lang)
    chm_site.set_bundle(bundles.get(bundle_name))
    self._setObject(id, chm_site)
    chm_site = self._getOb(id)
    chm_site.loadDefaultData(load_glossaries, _get_skel_handler(bundle_name))

    if google_api_keys:
        engine = chm_site.getGeoMapTool()['engine_google']
        engine.api_keys = google_api_keys

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

chm_bundle = bundles.get("CHM")
chm_bundle.set_parent(bundles.get("Naaya"))
chm3_bundle = bundles.get("CHM3")
chm3_bundle.set_parent(bundles.get("Naaya"))

class CHMSite(NySite):
    """ """
    implements(ICHMSite)
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
        self.show_releasedate = 1
        super(CHMSite, self).__init__(*args, **kwargs)
        self.set_bundle(chm_bundle)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, load_glossaries=[], skel_handler=None):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #remove Naaya default content
        layout_tool = self.getLayoutTool()
        naaya_skins = [skin.getId() for skin in
            layout_tool.objectValues('Naaya Skin')]
        logos = [image.getId() for image in
            layout_tool.objectValues('Image')]
        layout_tool.manage_delObjects(naaya_skins + logos)

        #load site skeleton - configuration
        if skel_handler is not None:
            self._load_skel_from_handler(skel_handler)

        #set default PhotoFolder
        addNyPhotoGallery(self, id='PhotoGallery', title=TITLE_PHOTOARCHIVE)
        self._getOb('PhotoGallery').approveThis()

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

        # enable some notifications
        self['portal_notification'].config['enable_monthly'] = True

        portal_layout = self['portal_layout']
        if 'chm3' in portal_layout.objectIds():
            portal_layout['chm3']._setProperty('main_section_image_size', '978x75')
            portal_layout['chm3']._setProperty('slider_image_size', '978x240')

    def get_data_path(self):
        """ """
        return CHM2_PRODUCT_PATH

    security.declareProtected(view_management_screens, 'add_glossary_coverage')
    def add_glossary_coverage(self):
        manage_addGlossaryCentre(self, ID_GLOSSARY_COVERAGE, TITLE_GLOSSARY_COVERAGE)
        glossary = self._getOb(ID_GLOSSARY_COVERAGE)

        skel_dump_path = os.path.join(CHM2_PRODUCT_PATH, 'skel', 'others',
                                      'coverage_glossary_translations')
        dump_data = glossary_dump_from_skel(skel_dump_path)
        glossary.dump_import(dump_data)

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

    def getPhotoArchive(self):
        ob = self._getOb('PhotoGallery', None)
        if ob is None:
            ob = self._getOb('PhotoArchive', None)
        return ob

    def getNewsArchive(self): return self._getOb('news', None)
    def getEventsArchive(self): return self._getOb('events', None)

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

    def _get_mainsection_images_folder(self):
        layout_tool = self.getLayoutTool()
        # not using get_current_skin to make it work for CHMBE
        skin = layout_tool._getOb(layout_tool.getCurrentSkinId()) # to work for CHMBE
        # add images folder if it doesn't exist
        if not skin.hasObject('main_section_images'):
            manage_addFolder(skin, 'main_section_images')
        return skin._getOb('main_section_images')

    def _get_slider_images_folder(self):
        layout_tool = self.getLayoutTool()
        # not using get_current_skin to make it work for CHMBE
        skin = layout_tool._getOb(layout_tool.getCurrentSkinId()) # to work for CHMBE
        # add images folder if it doesn't exist
        if not skin.hasObject('slider-images'):
            manage_addFolder(skin, 'slider-images')
        return skin._getOb('slider-images')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'upload_maintopic_temp_image')
    def upload_maintopic_temp_image(self, REQUEST):
        """ """
        temp_folder = self.getSite().temp_folder
        file = REQUEST.form.get("upload_file", None)
        if file is None:
            return json_response({'error': "no file"}, REQUEST.RESPONSE)

        filename = file.filename
        id = make_id(temp_folder, id=filename)
        manage_addImage(temp_folder, id, file=file)
        ob = getattr(temp_folder, id)

        skin = self.getLayoutTool().getCurrentSkin()
        image_size = map(int, skin.main_section_image_size.split("x"))

        try:
            data = crop_image(ob, image_size)
        except AssertionError, e:
            data = {"error": str(e)}

        return json_response(data, REQUEST.RESPONSE)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'upload_slider_temp_image')
    def upload_slider_temp_image(self, REQUEST):
        """ """
        temp_folder = self.getSite().temp_folder
        file = REQUEST.form.get("upload_file", None)
        if file is None:
            return json_response({'error': "no file"}, REQUEST.RESPONSE)

        filename = file.filename
        id = make_id(temp_folder, id=filename)
        manage_addImage(temp_folder, id, file=file)
        ob = getattr(temp_folder, id)

        skin = self.getLayoutTool().getCurrentSkin()
        skin_image_size = getattr(skin, 'slider_image_size', '978x240')
        image_size = map(int, skin_image_size.split("x"))

        try:
            data = crop_image(ob, image_size)
        except AssertionError, e:
            data = {"error": str(e)}

        return json_response(data, REQUEST.RESPONSE)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'load_current_maintopic_image')
    def load_current_maintopic_image(self, REQUEST):
        """ """
        main_section_images = self._get_mainsection_images_folder()
        name = REQUEST.form.get("name", None)
        ob = main_section_images._getOb(name, None)

        skin = self.getLayoutTool().getCurrentSkin()
        image_size = map(int, skin.main_section_image_size.split("x"))

        try:
            assert ob is not None, "no current image"
            # will throw an AssertionEerror if image is not valid
            data = crop_image(ob, image_size)
        except AssertionError, e:
            data = {"error": str(e)}

        return json_response(data, REQUEST.RESPONSE)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'load_current_slider_image')
    def load_current_slider_image(self, REQUEST):
        """ """
        slider_images = self._get_slider_images_folder()
        name = REQUEST.form.get("name", None)
        ob = slider_images._getOb(name, None)

        skin = self.getLayoutTool().getCurrentSkin()
        skin_image_size = getattr(skin, 'slider_image_size', '978x240')
        image_size = map(int, skin_image_size.split("x"))

        try:
            assert ob is not None, "no current image"
            # will throw an AssertionEerror if image is not valid
            data = crop_image(ob, image_size)
        except AssertionError, e:
            data = {"error": str(e)}

        return json_response(data, REQUEST.RESPONSE)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, '_admin_save_image')
    def _admin_save_image(self, picture_id, upload_picture_url,
            x1, y1, x2, y2, width, height, def_width, def_height,
            container_folder, REQUEST=None, title='', subtitle=''):
        """ """

        if width and height:
            F_WIDTH = width
            F_HEIGHT = height
        else:
            F_WIDTH = def_width
            F_HEIGHT = def_height

        temp_folder = self.getSite().temp_folder

        upload_picture_url = urllib.unquote(upload_picture_url)
        # fetch image from temp folder or from container_folder folder
        if upload_picture_url.startswith(temp_folder.absolute_url()):
            folder =  temp_folder
        elif upload_picture_url.startswith(container_folder.absolute_url()):
            folder = container_folder
        else:
            raise ValueError()

        # get image
        new_picture = upload_picture_url.split('/')[-1]
        picture = folder[new_picture]
        if not picture_id:
            picture_id = new_picture

        # crop image
        crop_coordinates = (x1, y1, x2, y2)
        croped_picture = process_picture(picture, crop_coordinates,
                                        F_WIDTH, F_HEIGHT)

        # remove old image if exists
        if container_folder.hasObject(picture_id):
            container_folder.manage_delObjects([picture_id])

        # add image to folder
        if title or subtitle:
            picture_title = '%s|%s' % (title, subtitle)
        else:
            picture_title = ''
        manage_addImage(container_folder, picture_id, croped_picture,
                        title=picture_title)

        self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_savemaintopic_image')
    def admin_savemaintopic_image(self, mainsection, upload_picture_url,
            x1, y1, x2, y2, width, height, REQUEST=None):
        """ """
        def_width = 978
        def_height = 75
        main_section_images = self._get_mainsection_images_folder()
        self.inherit_mainsection_image = REQUEST.has_key(
                                            'inherit_mainsection_image')
        self._p_changed = True

        return self._admin_save_image(mainsection, upload_picture_url,
            x1, y1, x2, y2, width, height, def_width, def_height,
            main_section_images, REQUEST)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_save_slider_image')
    def admin_save_slider_image(self, sliderimage, upload_picture_url,
            x1, y1, x2, y2, width, height, picture_title, picture_subtitle,
            delete_picture=None, REQUEST=None):
        """ """

        if delete_picture:
            return self.admin_delete_slider_image(sliderimage, REQUEST)

        if width and height:
            skin = self.getLayoutTool().getCurrentSkin()
            setattr(skin, 'slider_image_size', '%sx%s' % (width, height))

        def_width = 978
        def_height = 240
        slider_images = self._get_slider_images_folder()

        return self._admin_save_image(sliderimage, upload_picture_url,
            x1, y1, x2, y2, width, height, def_width, def_height,
            slider_images, REQUEST, picture_title, picture_subtitle)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_delete_slider_image')
    def admin_delete_slider_image(self, sliderimage, REQUEST=None):
        """ """

        slider_images = self._get_slider_images_folder()
        slider_images.manage_delObjects([sliderimage])

        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(view, 'getSliderImages')
    def getSliderImages(self):
        """
        Returns a list of the ids of all slider images
        """
        skin = self.getLayoutTool().getCurrentSkin()
        if 'slider-images' in skin.objectIds():
            return [ob for ob in skin['slider-images'].objectValues('Image')]
        else:
            return []

    security.declareProtected(view, 'get_mainsection')
    def get_mainsection(self, ob):
        """
        Returns the main section to which an object belongs (hierarchically)
        or None if the object resides outside main sections
        """
        if ob == self:
            return ''
        if ob.aq_parent == self:
            ob_id = ob.getId()
            if ob_id in self.maintopics:
                return ob_id
            else:
                return ''
        else:
            return self.get_mainsection(ob.aq_parent)

    security.declareProtected(view, 'show_mainsection_image')
    def show_mainsection_image(self, ob):
        """
        Returns true/false - should the main section image be shown
        in the current folder (based on inherit_mainsection_image flag)
        """
        mainsection = self.get_mainsection(ob)

        if not mainsection:
            return False
        elif ob.getId() == mainsection:
            return True
        elif getattr(self, 'inherit_mainsection_image', True):
            return True

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
        'separator': '|',
    }

    if schema.getId() == 'NyMunicipality':
        return
    elif schema.getId() == 'NyExpert':
        prop_spec['sortorder'] = 215

    if schema.getId() in ['NyExpert', 'NyOrganisation', 'NyProject']:
        prop_spec['visible'] = True

    if schema.getId() in ['NyProject', 'NyOrganisation']:
        prop_spec['label'] = 'Main topics covered'
    elif schema.getId() == 'NyExpert':
        prop_spec['label'] = 'Main areas of expertise'

    schema.addWidget('chm_terms', **prop_spec)

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

def process_picture(picture, crop_coordinates, F_WIDTH, F_HEIGHT):
    image_string = picture2stringIO(picture)
    img = Image.open(image_string)
    fmt = img.format
    if fmt.lower() in ['bmp', 'tiff']:
        fmt = 'JPEG'
    crop_size = F_WIDTH
    if crop_coordinates[2] - crop_coordinates[0] == 0:
        x = img.size[0]
        y = img.size[1]
        if F_HEIGHT * x > F_WIDTH * y:
            crop_coordinates = ((x - F_WIDTH * y / F_HEIGHT) / 2, 0, (x + F_WIDTH * y / F_HEIGHT) / 2, y)
        else:
            crop_coordinates = (0, (y - (F_HEIGHT * x / F_WIDTH)) / 2, x, (y + (F_HEIGHT * x / F_WIDTH)) / 2)

    img = img.crop(crop_coordinates)
    try:
        img = img.resize((F_WIDTH, F_HEIGHT), Image.ANTIALIAS)
    except AttributeError:
        img = img.resize((F_WIDTH, F_HEIGHT))
    newimg = StringIO()
    img.save(newimg, fmt, quality=85)
    return newimg.getvalue()

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

def crop_image(ob, image_default_size):
    image_file = picture2stringIO(ob)
    image_size = get_image_size(image_file)

    assert image_size, "can't determine image size"

    x, y = image_size[0], image_size[1]
    title = ob.title
    if '|' not in ob.title:
        title = '%s|' % ob.title
    if (image_default_size[1] * x) > (image_default_size[0] * y):
        data = {
            'url': ob.absolute_url(),
            'x': (x - image_default_size[0] * y / image_default_size[1]) / 2,
            'y': 0,
            'x2': (x + image_default_size[0] * y / image_default_size[1]) / 2,
            'y2': y,
            'title': title,
        }
    else:
        data = {
            'url': ob.absolute_url(),
            'x': 0,
            'y': (y - (image_default_size[1] * x / image_default_size[0])) / 2,
            'x2': x,
            'y2': (y + (image_default_size[1] * x / image_default_size[0])) / 2,
            'title': title,
        }

    return data


def picture2stringIO(picture):
    # TODO use tempfile.TemporaryFile or tempfile.SpooledTemporaryFile
    str_data = StringIO()
    for buf in iter_file_data(picture):
        str_data.write(buf)
    str_data.seek(0)
    return str_data


style_preview_template = PageTemplateFile('zpt/style_preview', globals())

class StylePreview(BrowserPage):
    def __call__(self, REQUEST):
        context = self.aq_parent
        page = 'no-portlets'
        return style_preview_template.__of__(context)(page=page)
