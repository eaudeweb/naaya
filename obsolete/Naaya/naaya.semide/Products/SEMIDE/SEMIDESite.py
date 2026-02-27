from random import choice
import os
import xmlrpclib

#Zope imports
from DateTime import DateTime
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass
from OFS.Cache import Cacheable
from OFS.Image import Image, manage_addImage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from ZPublisher.HTTPRequest import record
from zope.interface import implements

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *

from naaya.content.document import document_item; METATYPE_NYDOCUMENT = document_item.config['meta_type']
from naaya.content.semide.document import semdocument_item; METATYPE_NYSEMDOCUMENT = semdocument_item.config['meta_type']
from naaya.content.semide.country import country_item; METATYPE_NYCOUNTRY = country_item.config['meta_type']
from naaya.content.semide.event import semevent_item; METATYPE_NYSEMEVENT = semevent_item.config['meta_type']
from naaya.content.semide.fieldsite import semfieldsite_item; METATYPE_NYSEMFIELDSITE = semfieldsite_item.config['meta_type']
from naaya.content.semide.funding import semfunding_item; METATYPE_NYSEMFUNDING = semfunding_item.config['meta_type']
from naaya.content.semide.multimedia import semmultimedia_item; METATYPE_NYSEMMULTIMEDIA = semmultimedia_item.config['meta_type']
from naaya.content.semide.news import semnews_item; METATYPE_NYSEMNEWS = semnews_item.config['meta_type']
from naaya.content.semide.organisation import semorganisation_item; METATYPE_NYSEMORGANISATION = semorganisation_item.config['meta_type']
from naaya.content.semide.project import semproject_item; METATYPE_NYSEMPROJECT = semproject_item.config['meta_type']
from naaya.content.semide.textlaws import  semtextlaws_item; METATYPE_NYSEMTEXTLAWS = semtextlaws_item.config['meta_type']
from naaya.content.semide.thematicdir import semthematicdir_item; METATYPE_NYSEMTHEMATICDIR = semthematicdir_item.config['meta_type']


from Products.NaayaProfilesTool.ProfileMeta import ProfileMeta
from Products.NaayaProfilesTool.constants import ID_PROFILESTOOL
from Products.NaayaProfilesTool.ProfilesTool import manage_addProfilesTool

from Products.Naaya.managers.skel_parser import skel_handler_for_path
from Products.Naaya.NySite                          import NySite
from Products.Naaya.NySite                          import CONTAINERS_METATYPES
from Products.Naaya.NySite                    import NAAYA_CONTAINERS_METATYPES
from Products.NaayaCore.managers.paginator import ObjectPaginator
from Products.NaayaCore.managers.utils              import utils, tmpfile
from Products.NaayaCore.managers.utils              import file_utils, batch_utils
from Products.NaayaCore.managers.search_tool        import ProxiedTransport

from Products.Naaya.NyFolder                        import addNyFolder
from Products.Naaya.adapters                        import FolderMetaTypes
from Products.NaayaCalendar.EventCalendar           import manage_addEventCalendar
from Products.NaayaCore.managers.paginator          import ObjectPaginator
from Products.NaayaForum.NyForum                    import addNyForum
from Products.NaayaForum.constants                  import METATYPE_NYFORUM, METATYPE_NYFORUMTOPIC, METATYPE_NYFORUMMESSAGE
from Products.NaayaGlossary.NyGlossary              import manage_addGlossaryCentre
from Products.NaayaGlossary.constants               import NAAYAGLOSSARY_CENTRE_METATYPE
from Products.NaayaLinkChecker.LinkChecker          import manage_addLinkChecker
from Products.NaayaPhotoArchive.NyPhotoGallery      import addNyPhotoGallery
from Products.NaayaPhotoArchive.constants           import METATYPE_NYPHOTOGALLERY
from Products.NaayaThesaurus.NyThesaurus            import manage_addThesaurus
from Products.NaayaThesaurus.constants              import NAAYATHESAURUS_METATYPE
from Products.RDFCalendar.RDFCalendar               import manage_addRDFCalendar
from Products.PythonScripts.PythonScript import manage_addPythonScript
from Products.ZOpenArchives import (OAIServer, OAIAggregator,
                                    ZCatalogHarvester,OAIHarvester)

from naaya.component import bundles

from interfaces import ISEMIDESite

from managers.config_parser                         import config_parser
from managers.semide_zip                            import SemideZip
from managers                                       import utils as semide_utils
from managers.decorators                            import cachable, content_type_xml

from pdf.export_pdf                                 import export_pdf
from Tools.FlashTool                                import manage_addFlashTool
import logging

logger = logging.getLogger('SEMIDESite')

try:
    import memcache
    MC = memcache.Client(['127.0.0.1:11211'], debug=0)
except ImportError:
    MC = None
    logger.warning("No memcache support. Make sure the python-memcache is"
                    "installed and the server is running")

# TODO: these should stay only in naaya containers,
# but it seems they are used here
CONTAINERS_METATYPES.extend([METATYPE_NYCOUNTRY,
                             METATYPE_NYPHOTOGALLERY,
                             METATYPE_NYSEMTHEMATICDIR])
NAAYA_CONTAINERS_METATYPES.extend([METATYPE_NYCOUNTRY,
                                   METATYPE_NYPHOTOGALLERY,
                                   METATYPE_NYSEMTHEMATICDIR])

def _get_skel_handler(bundle_name):
    if bundle_name == 'SEMIDE':
        skel_path = os.path.join(SEMIDE_PRODUCT_PATH, 'skel')
        return skel_handler_for_path(skel_path)

manage_addSEMIDESite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addSEMIDESite(self, id='', title='', lang=None, bundle_name='SEMIDE',
                         REQUEST=None):
    """ """
    ut = utils()
    id = ut.utSlugify(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    semide_site = SEMIDESite(id, title=title, lang=lang)
    semide_site.set_bundle(bundles.get(bundle_name))
    self._setObject(id, semide_site)
    semide_site = self._getOb(id)
    semide_site.loadDefaultData(_get_skel_handler(bundle_name))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

semide_bundle = bundles.get("SEMIDE")
semide_bundle.set_parent(bundles.get("Naaya"))

class SEMIDESite(NySite, ProfileMeta, export_pdf, SemideZip, Cacheable):
    """ """
    implements(ISEMIDESite)
    meta_type = METATYPE_SEMIDESITE
    icon = 'misc_/SEMIDE/Site.gif'

    manage_options = (
        NySite.manage_options
        +
        Cacheable.manage_options
    )

    security = ClassSecurityInfo()

    product_paths = NySite.product_paths + [SEMIDE_PRODUCT_PATH]


    def __init__(self, *args, **kwargs):
        """ """
        self.show_releasedate = 1
        super(SEMIDESite, self).__init__(*args, **kwargs)

    def _configure_linkchecker(self, linkchecker_ob):
        # Add Naaya Folder content type to be checked by linkchecker
        linkchecker_ob.manage_addMetaType('Naaya Folder')
        linkchecker_ob.manage_addProperty('Naaya Folder', 'description', multilingual=1)

        # Add all installed content types to be checked by linkchecker
        ctypes = linkchecker_ob.get_pluggable_installed_meta_types()
        for ctype in ctypes:
            if ctype == 'Naaya URL':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya URL', 'locator',islink=1)
            elif ctype == 'Naaya Semide Document':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Document', 'source_link', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Semide Document', 'file_link', islink=1)
            elif ctype == 'Naaya Country Folder':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'nfp_url', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'link_ins', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'link_doc', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'link_train', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'link_rd', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'link_data', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'legislation_feed_url', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Country Folder', 'project_feed_url', islink=1)
            elif ctype == 'Naaya Semide Multimedia':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Multimedia', 'source_link', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Semide Multimedia', 'file_link', islink=1)
            elif ctype == 'Naaya Semide Text of Laws':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Text of Laws', 'source_link', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Semide Text of Laws', 'file_link', islink=1)
            elif ctype == 'Naaya Semide Event':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Event', 'source_link', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Semide Event', 'file_link', islink=1)
            elif ctype == 'Naaya Extended File':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Extended File', 'url', islink=1)
            elif ctype == 'Naaya Pointer':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Pointer', 'pointer', islink=1)
            elif ctype == 'Naaya Semide Project':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Project', 'resourceurl', islink=1)
            elif ctype == 'Naaya Semide News':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide News', 'source_link', islink=1)
                linkchecker_ob.manage_addProperty('Naaya Semide News', 'file_link', islink=1)
            elif ctype == 'Naaya Semide Organization':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Organization', 'org_url', islink=1)
            elif ctype == 'Naaya Semide Publication':
                linkchecker_ob.manage_addMetaType(ctype)
                linkchecker_ob.manage_addProperty('Naaya Semide Publication', 'publication_url', islink=1)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, skel_handler=None):
        """ """
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #load site skeleton - configuration
        if skel_handler is not None:
            self._load_skel_from_handler(skel_handler)

        if self.getSyndicationTool()._getOb('news_rdf', None):
            self.getSyndicationTool().manage_delObjects('news_rdf')

        if self.getSyndicationTool()._getOb('lateststories_rdf', None):
            self.getSyndicationTool().manage_delObjects('lateststories_rdf')

        self.getLayoutTool().manage_delObjects('skin')

        manage_addProfilesTool(self)
        #overwrite default subobjects for folders
        #self.getPropertiesTool().manageSubobjects(subobjects=None, ny_subobjects=[x for x in self.get_meta_types(1) if x not in [METATYPE_NYSEMFIELDSITE, METATYPE_NYSEMFUNDING, METATYPE_NYSEMORGANISATION]])
        self.getPortletsTool().manage_delObjects('topnav_links')

        addNyPhotoGallery(self, ID_PHOTOARCHIVE, title=TITLE_PHOTOARCHIVE, contributor=self.getAuthenticationToolPath(1))

        #default RDF Calendar settings
        manage_addRDFCalendar(self, id=ID_RDFCALENDAR, title=TITLE_RDFCALENDAR, week_day_len=1)
        rdfcalendar_ob = self._getOb(ID_RDFCALENDAR)
        #adding local_events Script (Python)
        manage_addPythonScript(rdfcalendar_ob, 'local_events')
        local_events_ob = rdfcalendar_ob._getOb('local_events')
        local_events_ob._params = 'year=None, month=None, day=None'
        local_events_ob.write(open(os.path.dirname(__file__) + '/skel/others/local_events.py', 'r').read())

        manage_addLinkChecker(self, ID_LINKCHECKER, TITLE_LINKCHECKER)
        linkchecker_ob = self._getOb(ID_LINKCHECKER)
        linkchecker_ob.catalog_name = 'portal_catalog'
        linkchecker_ob.use_catalog = 1
        self._configure_linkchecker(linkchecker_ob)

        try:
            #set NFP private area
            nfp_private = self._getOb('nfp_private')
            nfp_private.setRestrictions('', 'Contributor')
        except:
            pass

        #set default thesaurus object
        manage_addThesaurus(self, ID_THESAURUS, TITLE_THESAURUS)
        thesaurus_ob = self._getOb(ID_THESAURUS)

        #set the flash tool
        manage_addFlashTool(self)

        #load default SKOS data on thesaurus
        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-themes-relations.xml'), 'r')
        thesaurus_ob.getConceptsFolder().skos_import(p_skos)

        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-relations.xml'), 'r')
        thesaurus_ob.getConceptRelationsFolder().skos_import(p_skos)

        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-themes-labels[en].xml'), 'r')
        thesaurus_ob.getThemesFolder().skos_import(p_skos, 'en')
        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-themes-labels[fr].xml'), 'r')
        thesaurus_ob.getThemesFolder().skos_import(p_skos, 'fr')
        try:
            p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-themes-labels[ar].xml'), 'r')
            thesaurus_ob.getThemesFolder().skos_import(p_skos, 'ar')
        except:
            pass

        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-labels[ar].xml'), 'r')
        thesaurus_ob.getTermsFolder().skos_import(p_skos, 'ar')
        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-labels[en].xml'), 'r')
        thesaurus_ob.getTermsFolder().skos_import(p_skos, 'en')
        p_skos = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'thesaurus-labels[fr].xml'), 'r')
        thesaurus_ob.getTermsFolder().skos_import(p_skos, 'fr')

        #create and fill glossaries
        manage_addGlossaryCentre(self, ID_GLOSSARY_COVERAGE, TITLE_GLOSSARY_COVERAGE)
        self._getOb(ID_GLOSSARY_COVERAGE).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_coverage[en].xml')))
        self._getOb(ID_GLOSSARY_COVERAGE).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_coverage[fr].xml')))
        self._getOb(ID_GLOSSARY_COVERAGE).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_coverage[ar].xml')))

        manage_addGlossaryCentre(self, ID_GLOSSARY_LANGUAGES, TITLE_GLOSSARY_LANGUAGES)
        self._getOb(ID_GLOSSARY_LANGUAGES).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_languages[en].xml')))

        manage_addGlossaryCentre(self, ID_GLOSSARY_RIVER_BASIN, TITLE_GLOSSARY_RIVER_BASIN)
        self._getOb(ID_GLOSSARY_RIVER_BASIN).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_river_basin[en].xml')))
        self._getOb(ID_GLOSSARY_RIVER_BASIN).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_river_basin[fr].xml')))
        self._getOb(ID_GLOSSARY_RIVER_BASIN).xliff_import(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'glossary_river_basin[ar].xml')))

        #set the default thesaurus on picklists
        self.admin_properties(show_releasedate=1, rename_id='', http_proxy='',
                              repository_url=ID_THESAURUS,
                              keywords_glossary=ID_GLOSSARY_COVERAGE,
                              coverage_glossary='',submit_unapproved='',
                              portal_url='', rdf_max_items=10)

        #set default calendar object
        manage_addEventCalendar(self, id=ID_CALENDAR, day_len='1', start_day=CALENDAR_STARTING_DAY, catalog=ID_CATALOGTOOL)

        #set default calendar css and images
        cal_ob = self._getOb(ID_CALENDAR)

        cal_ob.cal_meta_types = cal_ob.setCalMetaTypes(METATYPE_NYSEMEVENT)

        #add the images for sorted columns
        images_fld = self.getImagesFolder()

        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'sortup.gif'), 'rb')
        images_fld.manage_addImage(id='sortup.gif', title='SortUp', file='')
        images_fld._getOb('sortup.gif').update_data(data=content)

        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'sortdown.gif'), 'rb')
        images_fld.manage_addImage(id='sortdown.gif', title='SortDown', file='')
        images_fld._getOb('sortdown.gif').update_data(data=content)

        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'sortnot.gif'), 'rb')
        images_fld.manage_addImage(id='sortnot.gif', title='SortNot', file='')
        images_fld._getOb('sortnot.gif').update_data(data=content)

        #add flags for available languages
        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'flag_ar.gif'), 'rb')
        images_fld.manage_addImage(id='flag_ar.gif', title='ar', file='')
        images_fld._getOb('flag_ar.gif').update_data(data=content)

        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'flag_en.gif'), 'rb')
        images_fld.manage_addImage(id='flag_en.gif', title='en', file='')
        images_fld._getOb('flag_en.gif').update_data(data=content)

        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'flag_fr.gif'), 'rb')
        images_fld.manage_addImage(id='flag_fr.gif', title='fr', file='')
        images_fld._getOb('flag_fr.gif').update_data(data=content)

        #add image for pdf
        content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', 'pdf.gif'), 'rb')
        images_fld.manage_addImage(id='pdf.gif', title='PDF', file='')
        images_fld._getOb('pdf.gif').update_data(data=content)

        #custom configuration
        config = config_parser()
        config_handler, error = config_parser().parse(file_utils().futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'config.xml'), 'r'))
        if config_handler is not None:
            if config_handler.root.thumbs is not None:
                images_fld = self.getImagesFolder()
                images_fld.manage_addFolder(id='thumbs', title='Thums images')
                images_fld = self.getThumbsFolder()
                for thumb in config_handler.root.thumbs.thumbs:
                    id = 'thumb%s' % self.utGenRandomId(4)
                    content = self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others', thumb.id), 'rb')
                    images_fld.manage_addImage(id=id, title='', file='')
                    images_fld._getOb(id).update_data(data=content)

        #load pluggable profiles
        profilestool_ob = self.getProfilesTool()
        profilestool_ob.manageAddProfileMeta('')
        profilestool_ob.manageAddProfileMeta(ID_FLASHTOOL)

        #create and configure a forum
        addNyForum(self, id='forum', title='Forum', description='', categories=['General'])

        try:
            #set default main topics
            self.getPropertiesTool().manageMainTopics(['about', 'countries',
                'introduction', 'partners', 'initiatives', 'thematicdirs',
                'publications', 'documents', 'nfp_private', 'topics'])
        except:
            pass

        #Latest news portlet for about folder on the right side
        self.getPortletsTool().assign_portlet(self._getOb('about').absolute_url(1), 'right' 'portlet_latestnews_rdf', True)

        #set portal index's right portlets
        self.getPortletsTool().assign_portlet('', 'right', 'portlet_calendar')
        self.getPortletsTool().assign_portlet('', 'right', 'portlet_latestnews_rdf')
        self.getPortletsTool().assign_portlet('', 'right', 'portlet_upcomingevents_rdf')
        self.getPortletsTool().assign_portlet('', 'right', 'portlet_eflash')

        #do not show portlet title
        try: self.getPortletsTool()._getOb('portlet_maincategories').manage_addProperty('hide_title', 1, 'int')
        except: pass
        try: self.getPortletsTool()._getOb('portlet_left_logo').manage_addProperty('hide_title', 1, 'int')
        except: pass

        #add a new index in the Catalog
        try:    self.getCatalogTool().addIndex('resource_type', 'FieldIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('resource_status', 'FieldIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('resource_date', 'DateIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('resource_end_date', 'DateIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('start_date', 'DateIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('end_date', 'DateIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('news_date', 'DateIndex')
        except: pass
        class DateRangeIndexExtraParams: # 100% stupid code needed for DateRangeIndex
            def __init__(self, since_field, until_field):
                self.since_field = since_field
                self.until_field = until_field
        self.getCatalogTool().manage_addIndex('resource_interval', 'DateRangeIndex', extra=DateRangeIndexExtraParams('resource_date', 'resource_end_date'))
        try:    self.getCatalogTool().manage_addIndex('resource_subject', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass
        try:    self.getCatalogTool().addIndex('statute', 'FieldIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('geozone', 'FieldIndex')
        except: pass

        #SchemaTool custom configuration
        schema_tool = self.getSchemaTool()
        widget_args = dict(label="Tooltip", widget_type='String',
                           data_type='str')

        naaya_folder_schema = schema_tool.getSchemaForMetatype(METATYPE_FOLDER)
        if naaya_folder_schema:
            naaya_folder_schema.addWidget('tooltip', **widget_args)

        naaya_country_schema = schema_tool.getSchemaForMetatype(METATYPE_NYCOUNTRY)
        if naaya_country_schema:
            naaya_country_schema.addWidget('tooltip', **widget_args)

        #set searchable meta types
        sc = self.searchable_content
        sc.extend([METATYPE_NYFORUMTOPIC, METATYPE_NYFORUMMESSAGE])
        self.setSearchableContent(sc)

        #Adding OAI Functionality
        OAIServer.manage_addOAIServer(self, id="zoai",
                                      title=u"Zope OAI Server")
        OAIAggregator.manage_addOAIAggregator(self, id="oai_aggregator",
                                title=u"OAI Aggregator")
        zoai = self._getOb('zoai')
        ZCatalogHarvester.manage_addZCatalogHarvester(zoai,
            id='nws_portal_catalog', title=u'News OAI Provider',
            search_meta_types=[METATYPE_NYSEMNEWS])
        ZCatalogHarvester.manage_addZCatalogHarvester(zoai,
            id='evt_portal_catalog', title=u'Events OAI Provider',
            search_meta_types=[METATYPE_NYSEMEVENT])
        ZCatalogHarvester.manage_addZCatalogHarvester(zoai,
            id='doc_portal_catalog', title=u'Documents OAI Provider',
            search_meta_types=[METATYPE_NYDOCUMENT, METATYPE_NYSEMDOCUMENT,
                               METATYPE_NYSEMTEXTLAWS])

    def get_data_path(self):
        """ """
        return SEMIDE_PRODUCT_PATH

    security.declarePublic('get_constant')
    def get_constant(self, c): return eval(c)

    #objects getters
    def getPhotoArchive(self):              return self._getOb(ID_PHOTOARCHIVE, None)
    def getLinkChecker(self):               return self._getOb(ID_LINKCHECKER, None)
    def getSkinFilesPath(self):             return self.getLayoutTool().getSkinFilesPath()
    def getThumbsFolder(self):              return self.getImagesFolder()._getOb('thumbs')
    def getInitiativesFolder(self):         return self._getOb('initiatives')
    def getFlashTool(self):                 return self._getOb(ID_FLASHTOOL, None)
    def getFlashToolPath(self, p=0):        return self._getOb(ID_FLASHTOOL).absolute_url(p)
    def getFlashArchive(self):
        return self.unrestrictedTraverse(self.getFlashTool().archive_path, None)
    def getFlashArchivePath(self):
        archive = self.getFlashArchive()
        return archive.absolute_url()
    def getPortalThesaurus(self):           return self._getOb(ID_THESAURUS)
    def getRiverBasinGlossary(self):        return self._getOb(ID_GLOSSARY_RIVER_BASIN)

    def getCoverageGlossary(self):          return self._getOb(ID_GLOSSARY_COVERAGE)
    def getCoverageGlossaryObjects(self, lang_code=''):
        if not lang_code: lang_code = self.gl_get_selected_language()
        l_elems = []
        for k in self.getCoverageGlossary().folder_list_sorted():
            l_elems.extend(k.get_object_list())
        return self.getCoverageGlossary().utSortObjsListByAttr(l_elems, self.getCoverageGlossary().get_language_by_code(lang_code), 0)
    def getCoverageGlossaryTrans(self, p_id, lang_name):
        try:
            gloss_elem = self.getCoverageGlossary().cu_search_catalog_by_id(p_id)
            return gloss_elem[0].getObject().get_translation_by_language(lang_name)
        except:
            return ''

    def getLanguagesGlossary(self):         return self._getOb(ID_GLOSSARY_LANGUAGES)
    def getLanguagesGlossaryObjects(self, lang_code=''):
        if not lang_code: lang_code = self.gl_get_selected_language()
        l_elems = []
        for k in self.getLanguagesGlossary().folder_list_sorted():
            l_elems.extend(k.get_object_list())
        return self.getLanguagesGlossary().utSortObjsListByAttr(l_elems, self.getLanguagesGlossary().get_language_by_code(lang_code), 0)
    def getLanguagesGlossaryTrans(self, p_id, lang_name):
        try:
            gloss_elem = self.getLanguagesGlossary().cu_search_catalog_by_id(p_id)
            return gloss_elem[0].getObject().get_translation_by_language(lang_name)
        except:
            return ''

    def getLinkCheckerLastLog(self):
        entries = self.utSortObjsListByAttr(self._getOb(ID_LINKCHECKER).objectValues('LogEntry'), 'date_create', p_desc=1)
        if len(entries) > 0: return entries[0]
        else: return None


    security.declareProtected(view, 'process_profile')
    def process_profile(self, firstname='', lastname='', email='', name='', old_pass='', password='',
        confirm='', REQUEST=None):
        """ """
        err = ''
        success = False
        auth_user = REQUEST.AUTHENTICATED_USER.getUserName()
        user = self.getAuthenticationTool().getUser(auth_user)
        if password == '': password = confirm = old_pass
        if user._getPassword() == old_pass:
            try:
                self.getAuthenticationTool().manage_changeUser(name, password, confirm, [], [], firstname,              lastname, email)
                self.credentialsChanged(name, password)
                #keep authentication
            except Exception, error:
                err = error
            else:
                success = True
        else:
            err = WRONG_PASSWORD
        if REQUEST:
            if err != '': self.setSessionErrorsTrans(err)
            if success: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/profile_html' % self.absolute_url())

    security.declareProtected(view, 'profile_html')
    def profile_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_userprofile')

    security.declarePublic('getProfilesTool')
    def getProfilesTool(self): return self._getOb(ID_PROFILESTOOL)

    security.declarePublic('getProfilesToolPath')
    def getProfilesToolPath(self, p=0): return self._getOb(ID_PROFILESTOOL).absolute_url(p)

    #layer over the Localizer and MessageCatalog
    #the scope is to centralize the list of available languages
    def gl_add_site_language_custom(self, language):
        #this is called to handle other types of multilanguage objects
        self.getCatalogTool().add_index_for_lang('coverage', language)
        self.getCatalogTool().add_index_for_lang('programme', language)
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
            except: pass

    def gl_del_site_languages_custom(self, languages):
        #this is called to handle other types of multilanguage objects
        catalogtool_ob = self.getCatalogTool()
        for language in languages:
            catalogtool_ob.del_index_for_lang('coverage', language)
            catalogtool_ob.del_index_for_lang('programme', language)
        for gloss in self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            for language in languages:
                try:
                    gloss.del_language_from_list(language)
                    gloss._p_changed = 1
                except:
                    pass

    def get_resources(self):
        """ return the resources """
        return ['text of law', 'document', 'multimedia']

    def convertToFullURL(self, p_URL):
        p_URL = p_URL.strip()
        try:    p_URL = p_URL.encode('utf-8', 'ignore')
        except: pass
        if p_URL=='' or p_URL=='http://' or p_URL=='https://':
            return ''
        try:
            l_ob = self.unrestrictedTraverse(p_URL)
            return l_ob.absolute_url()
        except:
            return p_URL

    #layer over selection lists
    security.declarePublic('getEventStatusList')
    def getEventStatusList(self):
        """
        Return the selection list for event status.
        """
        return self.getPortletsTool().getRefTreeById('event_status').get_list()

    security.declarePublic('getEventStatusTitle')
    def getEventStatusTitle(self, id):
        """
        Return the title of an item for the selection list for event status.
        """
        try:
            return self.getPortletsTool().getRefTreeById('event_status').get_item(id).title
        except:
            return ''

    security.declarePublic('getTextLawsTypesList')
    def getTextLawsTypesList(self):
        """
        Return the selection list for text laws types.
        """
        return self.getPortletsTool().getRefTreeById('text_laws').get_list()

    security.declarePublic('getLawsStatusList')
    def getLawsStatusList(self):
        """
        Return the selection list for statuses types.
        """
        return self.getPortletsTool().getRefTreeById('status_types').get_list()

    security.declarePublic('getDocumentTypesList')
    def getDocumentTypesList(self):
        """
        Return the selection list for document types.
        """
        return self.getPortletsTool().getRefTreeById('document_types').get_list()

    security.declarePublic('getMultimediaTypesList')
    def getMultimediaTypesList(self):
        """
        Return the selection list for document types.
        """
        return self.getPortletsTool().getRefTreeById('multimedia_types').get_list()

    security.declarePublic('getNewsTypesList')
    def getNewsTypesList(self):
        """
        Return the selection list for news types.
        """
        return self.getPortletsTool().getRefTreeById('news_types').get_list()

    security.declarePublic('getNewsTypeTitle')
    def getNewsTypeTitle(self, id):
        """
        Return the title of an item for the selection list for news type.
        """
        try:
            return self.getPortletsTool().getRefTreeById('news_types').get_item(id).title
        except:
            return ''

    security.declarePublic('getGeozoneList')
    def getGeozoneList(self):
        """
        Return the selection list for object subject.
        """
        return self.getPortletsTool().getRefTreeById('event_geozone').get_list()

    security.declarePublic('getOrganismTypesList')
    def getOrganismTypesList(self):
        """
        Return the selection list for organism types.
        """
        return self.getPortletsTool().getRefTreeById('organism_types').get_list()

    security.declarePublic('getEventStatusTitle')
    def getOrganismTypeTitle(self, id):
        """
        Return the title of an item for the selection list for organism type.
        """
        try:
            return self.getPortletsTool().getRefTreeById('organism_types').get_item(id).title
        except:
            return ''

    security.declarePublic('getFundingTypesList')
    def getFundingTypesList(self):
        """
        Return the selection list for funding types.
        """
        return self.getPortletsTool().getRefTreeById('funding_types').get_list()

    security.declarePublic('getFundingTypeTitle')
    def getFundingTypeTitle(self, id):
        """
        Return the title of an item for the selection list for funding type.
        """
        try:
            return self.getPortletsTool().getRefTreeById('funding_types').get_item(id).title
        except:
            return ''

    security.declarePublic('getRightsTypesList')
    def getRightsTypesList(self):
        """
        Return the selection list for rights types.
        """
        return self.getPortletsTool().getRefTreeById('rights_types').get_list()

    #api
    def list_glossaries(self):
        #return all the glossaries in this portal
        return self.objectValues([NAAYAGLOSSARY_CENTRE_METATYPE, NAAYATHESAURUS_METATYPE])

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

    security.declareProtected(view, 'getNewsListing')
    def getNewsListing(self, query='', languages=[], nt='', nd='', nc='', skey='',
                       rkey='', ps_start='', p_context=None, **kwargs):
        """ Returns a list of news
        Use memcache if available.

        """
        results = []
        #get country list
        gz = kwargs.get('gz', [])
        if not isinstance(gz, list):
            gz = [gz]
        try:    ps_start = int(ps_start)
        except: ps_start = 0
        catalog_tool = self.getCatalogTool()
        search_args = {
            'meta_type': [METATYPE_NYSEMNEWS],
            'approved': 1,
            'sort_on': skey,
            'sort_order': rkey == '1' and 'descending' or 'ascending'
        }
        if query == '' and nt == '' and nd == '' and gz == []:
            #no criteria then returns the 10 more recent
            brains = catalog_tool(**search_args)
        else:
            query = self.utStrEscapeForSearch(query)
            if languages: langs = languages
            else: langs = [self.gl_get_selected_language()]
            #Fulltext query
            for lang in langs:
                search_args['objectkeywords_' + lang] = query
            #Geographical coverage
            if gz:
                for lang in langs:
                    for g in gz:
                        lang_name = self.gl_get_language_name(lang)
                        gz_trans = self.getCoverageGlossaryTrans(g, lang_name)
                        search_args['coverage_' + lang] = gz_trans
            #Type
            if nt:
                search_args['resource_type'] = nt
            #Date
            if nd:
                search_args['resource_date'] = nd
                if int(nc):
                    search_args['resource_date_range'] = 'min'
                else:
                    search_args['resource_date_range'] = 'max'
            brains = catalog_tool(**search_args)

        return brains

    security.declareProtected(view, 'sortResource')
    def sortResource(self, p_objects=[], skey='', rkey=''):
        #returns a sorted list of resources
        results = []
        if not skey or skey == 'date':
            p_objects.sort(lambda x,y: cmp(y.releasedate, x.releasedate) \
                           or cmp(x.sortorder, y.sortorder))
            if not rkey: p_objects.reverse()
            results.extend(p_objects)
        else:
            if rkey: rkey=1
            l_objects = semide_utils.utSortObjsByLocaleAttr(p_objects, skey, rkey, self.gl_get_selected_language())
            results.extend(l_objects)
        return results

    security.declareProtected(view, 'getResourceListing')
    def getResourceListing(self, query='', meta_types=[], textlaws_props=[], document_props=[],
                           multimedia_props=[], sd=None, ed=None, languages=[],
                           th='', skey='', rkey='', ps_start='', **kwargs):
        """
        Returns a list of resources
        """
        r = []
        res_per_page = kwargs.get('items', 10) or 10
        results = []
        dict = {}

        meta_types =        semide_utils.utConvertToListExact(meta_types)
        languages =         semide_utils.utConvertToListExact(languages)
        textlaws_props =    semide_utils.utConvertToListExact(textlaws_props)
        document_props =    semide_utils.utConvertToListExact(document_props)
        multimedia_props =  semide_utils.utConvertToListExact(multimedia_props)
        if th:  query_th = ', resource_subject=th'
        else:   query_th = ''
        if languages:   langs = languages
        else:           langs = self.gl_get_languages()

        query = self.utStrEscapeForSearch(query)
        l_query = 'approved=1%s' % query_th
        sd = self.utConvertStringToDateTimeObj(sd)
        ed = self.utConvertStringToDateTimeObj(ed)
        if sd and ed:
            l_query += ', resource_date=[sd, ed], resource_date_range=\'minmax\''
        elif sd:
            l_query += ', resource_date=sd, resource_date_range=\'min\''
        elif ed:
            l_query += ', resource_date=ed, resource_date_range=\'max\''

        for lang in langs:
            if query: l_query += ', objectkeywords_%s=query' % lang
            if METATYPE_NYSEMMULTIMEDIA in meta_types:
                mt_type = []
                mt_query = l_query
                if multimedia_props: mt_type.extend(multimedia_props)
                if mt_type: mt_query = l_query + ', resource_type=mt_type'
                expr = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSEMMULTIMEDIA], %s)' % mt_query
                r.extend(eval(expr))
            if METATYPE_NYSEMDOCUMENT in meta_types:
                dc_type = []
                dc_query = l_query
                if document_props: dc_type.extend(document_props)
                if dc_type: dc_query = l_query + ', resource_type=dc_type'
                expr = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSEMDOCUMENT], %s)' % dc_query
                r.extend(eval(expr))
            if METATYPE_NYSEMTEXTLAWS in meta_types:
                tl_type = []
                tl_query = l_query
                if textlaws_props: tl_type.extend(textlaws_props)
                if tl_type: tl_query = l_query + ', resource_type=tl_type'
                expr = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSEMTEXTLAWS], %s)' % tl_query
                r.extend(eval(expr))

        dict = {}
        for x in r:
            dict[x.id] = x

        results = self.get_archive_listing(self.sortResource(dict.values(), skey, rkey))

        #batch related
        batch_obj = batch_utils(res_per_page, len(results[2]), ps_start)
        if len(results[2]) > 0:
            paging_informations = batch_obj.butGetPagingInformations()
        else:
            paging_informations = (-1, 0, 0, -1, -1, 0, res_per_page, [0])
        return (paging_informations, (results[0], results[1], results[2][paging_informations[0]:paging_informations[1]]))

    security.declareProtected(view, 'getRequestParams')
    def getRequestParams(self, REQUEST=None):
        """returns a REQUEST.QUERY_STRING (using REQUEST.form,
            REQUEST.form=REQUEST.QUERY_STRING as a dictionary)"""
        ignore_list = ['skey', 'rkey']
        res=''
        if REQUEST:
            for key in self.REQUEST.form.keys():
                if key not in ignore_list:
                    p_value = self.REQUEST.form[key]
                    if type(p_value) == type([]):
                        l_name = '&%s:list=' % key
                        p_all = l_name.join(p_value)
                        res = res + key + ':list=' + str(p_all) + '&'
                    else:
                        res = res + key + '=' + str(p_value) + '&'
        return res

    security.declareProtected(view, 'getEventsListing')
    def getEventsListing(self, query='', languages=[], et='', gz='', es='', skey='',
                         rkey=0, sd='', ed='', p_context=None,
                         ps_start='', **kwargs):
        """ Returns a list of events """
        if gz != '' and not isinstance(gz, list):
            gz = [gz]
        try:    ps_start = int(ps_start)
        except: ps_start = 0
        if skey not in ('start_date', ):
            skey = 'start_date'
        catalog_tool = self.getCatalogTool()
        search_args = {
            'meta_type': [METATYPE_NYSEMEVENT],
            'approved': 1,
            'sort_on': skey,
            'sort_order': rkey == '1' and 'descending' or 'ascending'
        }
        if query == '' and et == '' and not gz and es == '' and sd == '' and ed == '':
            #no criteria then returns the 10 more recent
            brains = catalog_tool(**search_args)
        else:
            query = self.utStrEscapeForSearch(query)
            if languages: langs = languages
            else: langs = [self.gl_get_selected_language()]
            #Fulltext query
            for lang in langs:
                search_args['objectkeywords_' + lang] = query
            #Geographical coverage
            if gz:
                for lang in langs:
                    for g in gz:
                        lang_name = self.gl_get_language_name(lang)
                        gz_trans = self.getCoverageGlossaryTrans(g, lang_name)
                        search_args['coverage_' + lang] = gz_trans
            #Type
            sd = self.utConvertStringToDateTimeObj(sd)
            ed = self.utConvertStringToDateTimeObj(ed)
            if sd and ed:
                search_args['resource_date'] = [sd, ed]
                search_args['resource_date_range'] = 'minmax'
            elif sd:
                search_args['resource_date'] = sd
                search_args['resource_date_range'] = 'min'
            elif ed:
                search_args['resource_date'] = ed
                search_args['resource_date_range'] = 'max'
            if et:
                search_args['resource_type'] = et
            if es:
                search_args['resource_status'] = es
            brains = catalog_tool(**search_args)

        return brains

    security.declareProtected(view, 'getEventsNFP')
    def getEventsNFP(self, query='', languages=[], et='', gz='', es='', skey='', rkey=0, sd='', ed='', p_context=None, ps_start=''):
        """
        Returns a list of events
        """
        #default data
        results = []
        res_per_page = 10
        try:    ps_start = int(ps_start)
        except: ps_start = 0
        try:    l_archive = self.unrestrictedTraverse(p_context)
        except: l_archive = None

        if l_archive:
            if query == '' and et == '' and gz == '' and es == '' and sd == '' and ed == '':
                # no criteria then returns the 10 fore coming
                p_objects = [x for x in l_archive.objectValues('Naaya Semide Event') if x.start_date >= DateTime() and x.approved]
                results = self.get_archive_listing(self.sorted_events_listing(p_objects, skey, rkey))
            else:
                r = []
                query = self.utStrEscapeForSearch(query)
                l_query = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSEMEVENT], approved=1, path=\'/\'.join(l_archive.getPhysicalPath())'
                if et: l_query += ', resource_type=[et]'
                if es: l_query += ', resource_status=[es]'

                sd = self.utConvertStringToDateTimeObj(sd)
                ed = self.utConvertStringToDateTimeObj(ed)
                if sd and ed:
                    l_query += ', resource_date=[sd, ed], resource_date_range=\'minmax\''
                elif sd:
                    l_query += ', resource_date=sd, resource_date_range=\'min\''
                elif ed:
                    l_query += ', resource_date=ed, resource_date_range=\'max\''

                if languages: langs = languages
                else: langs = [self.gl_get_selected_language()]
                for lang in langs:
                    expr = l_query
                    if gz:
                        lang_name = self.gl_get_language_name(lang)
                        gz_trans = self.getCoverageGlossaryTrans(gz, lang_name)
                        expr += ', coverage_%s=gz_trans' % lang
                    if query: expr += ', objectkeywords_%s=query' % lang
                    expr += ')'
                    r.extend(eval(expr))
                dict = {}
                for x in r:
                    dict[x.id] = x
                results = self.get_archive_listing(self.sorted_events_listing(dict.values(), skey, rkey))
        else:
            return []

        #batch related
        batch_obj = batch_utils(res_per_page, len(results[2]), ps_start)
        if len(results[2]) > 0:
            paging_informations = batch_obj.butGetPagingInformations()
        else:
            paging_informations = (-1, 0, 0, -1, -1, 0, res_per_page, [0])
        return (paging_informations, (results[0], results[1], results[2][paging_informations[0]:paging_informations[1]]))

    security.declareProtected(view, 'sorted_projects_listing')
    def sorted_projects_listing(self, p_objects=[], skey='', rkey=0):
        """Return sorted projects"""
        results = []
        if not skey or skey == 'start_date':
            p_objects.sort(lambda x,y: cmp(y.start_date, x.start_date) \
                           or cmp(x.sortorder, y.sortorder))
            if not rkey: p_objects.reverse()
            results.extend(p_objects)
        else:
            if rkey: rkey=1
            l_objects = semide_utils.utSortObjsByLocaleAttr(p_objects, skey, rkey, self.gl_get_selected_language())
            results.extend(l_objects)
        return results

    def _getProjectsListing(self, query='', so='', languages=[], skey='', rkey=0,
                           archive=[], ps_start='', gz='', th='', pr='', **kwargs):
        """
        Returns a list of projects
        """
        r = []
        if not (query or so or gz or th or pr):
            #no criteria then returns the 10 more recent
            if not archive:
                p_context = kwargs.get('p_context', None)
                try:
                    archive = self.unrestrictedTraverse(p_context).getObjects()
                except:
                    return []
                else:
                    return archive
            return archive

        if languages:
            langs = languages
        else:
            langs = self.gl_get_languages()
        query_r = []
        so_r = []

        #search for projects
        if query or gz or th or pr:
            query = self.utStrEscapeForSearch(query)
            l_query = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSEMPROJECT], approved=1'
            if th: l_query += ', resource_subject=th'
            for lang in langs:
                expr = l_query
                if gz:
                    lang_name = self.gl_get_language_name(lang)
                    gz_trans = self.getCoverageGlossaryTrans(gz, lang_name)
                    expr += ', coverage_%s=gz_trans' % lang
                if pr:    expr += ', programme_%s=pr' % lang
                if query: expr += ', objectkeywords_%s=query' % lang
                expr += ')'
                query_r.extend(eval(expr))
        #search for organisations
        if so:
            org_list = []
            so_query = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSEMORGANISATION], approved=1'
            for lang in langs:
                expr = so_query
                if so: expr += ', objectkeywords_%s=so' % lang
                expr += ')'
                org_list.extend(eval(expr))
            for x in org_list:
                so_r.append(x.getParentNode())

        #merge the search results of projects and organisations
        if query and so:
            so_list = []
            for x in query_r:
                if x in so_r and x not in r:
                    r.append(x)
        else:
            r.extend(query_r)
            r.extend(so_r)
        return r

    security.declareProtected(view, 'getProjectsListing')
    def getProjectsListing(self, query='', so='', languages=[], skey='', rkey=0,
                           archive=[], ps_start='', gz='', th='', pr='', path='', **kwargs):
        """ Returns a list of brains """
        if gz != '' and not isinstance(gz, list):
            gz = [gz]
        try:    ps_start = int(ps_start)
        except: ps_start = 0
        if skey not in ('start_date', ):
            skey = 'start_date'
        catalog_tool = self.getCatalogTool()
        search_args = {
            'meta_type': [METATYPE_NYSEMPROJECT],
            'approved': 1,
            'sort_on': skey,
            'sort_order': rkey == '1' and 'descending' or 'ascending',
            'path': path
        }
        if languages: langs = languages
        else: langs = [self.gl_get_selected_language()]

        if not (query or so or gz or th or pr):
            brains = catalog_tool(**search_args)
        else:
            query = self.utStrEscapeForSearch(query)
            #Fulltext query
            for lang in langs:
                if query: search_args['objectkeywords_' + lang] = query
                if pr: search_args['programme_' +  lang] = pr
            #Geographical coverage
            if gz:
                for lang in langs:
                    for g in gz:
                        lang_name = self.gl_get_language_name(lang)
                        gz_trans = self.getCoverageGlossaryTrans(g, lang_name)
                        search_args['coverage_' + lang] = gz_trans
            if th:
                search_args['resource_subject'] = th
            brains = catalog_tool(**search_args)
            if so:
                project_ids = set([brain.id for brain in brains])
                search_args = {
                    'meta_type': [METATYPE_NYSEMORGANISATION],
                    'approved': 1,
                }
                for lang in langs:
                    search_args['objectkeywords_' + lang] = so
                project_ids = project_ids.intersection(
                    set([brain.getObject().aq_parent.getId()
                        for brain in catalog_tool(**search_args)]))
                brains = catalog_tool(id=list(project_ids))
        return brains

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getCSSEntity')
    def getCSSEntity(self, marker_start, merker_end):
        """ """
        scheme = self.getLayoutTool().getCurrentSkinScheme()
        style_src = scheme._getOb('style').document_src()
        start = style_src.find(marker_start)
        end = style_src.find(merker_end)
        color = style_src[start+len(marker_start):end]
        return color.strip()

    security.declareProtected(view, 'getThumbs')
    def getThumbs(self):
        """ """
        thumbs = self.get_thumbs()
        images = []
        results = []
        if len(thumbs):
            for i in range(3):
                try:
                    thumb = choice(thumbs)
                    thumbs.remove(thumb)
                    images.append(thumb)
                except:
                    images.append('')

            for item in images:
                if isinstance(item, Image):
                    results.append('%s/%s/%s/%s' % (self.getSitePath(), ID_IMAGESFOLDER, 'thumbs', item.getId()))
                else:
                    results.append('')
            return results
        else: return ['', '', '']

    def paggingContent(self, content):
        return ObjectPaginator(content, num_per_page=25, orphans=15)

    #left navigation related
    def getNavFolders(self, l_folder):
        #sort alphabeticaly if sortorder is the same.
        l_buff = self.utSortObjsListByAttr([x for x in l_folder.objectValues([METATYPE_FOLDER, METATYPE_NYCOUNTRY, METATYPE_NYPHOTOGALLERY, METATYPE_NYSEMTHEMATICDIR]) if (x.submitted==1 and x.approved==1)], "title", 0)
        return self.utSortObjsListByAttr(l_buff, "sortorder", 0)

    def _testIsRoot(self, p_location):
        """ test if location is the root """
        if p_location is None or p_location == self: return 1
        return 0

    def _getLocation(self, p_location):
        """ return the root or the NaayaFolder parent as location """
        if self._testIsRoot(p_location):
            return p_location
        else:
            if hasattr(p_location, 'meta_type') and (p_location.meta_type not in [METATYPE_FOLDER, METATYPE_NYCOUNTRY]):
                return self._getLocation(p_location.getParentNode())
            else:
                return p_location

    security.declareProtected(view, 'processNavigation')
    def processNavigation(self, p_location=None):
        """
        Returns a list that will be used to display the navigation menu.
        The list contains folder objects
        """
        #set location as the parent NaayaFolder or the root if location is different than that
        p_location = self._getLocation(p_location)
        if self._testIsRoot(p_location):
            #if we are in the root of the portal nothing will be displayed
            return ([(x, 0) for x in self.getMainTopics()], None)
        else:
            #first test if the given location has as main parent a main folder
            l_mainfolder = self.getFolderMainParent(p_location)
            if l_mainfolder in self.getMainTopics():
                if l_mainfolder is p_location and l_mainfolder.id not in ['countries', 'partners', 'publications', 'documents']:  #coded for countries
                    return ([(x, 0) for x in self.getNavFolders(l_mainfolder)], l_mainfolder)
                else:
                    l = []
                    for x in self.getNavFolders(l_mainfolder):
                        childs = self.getNavFolders(x)
                        if p_location in childs:
                            buf = []
                            for y in childs:
                                if p_location == y: buf.append((y, 1))
                                else: buf.append((y, 0))
                            l.append(((x, 0), buf))
                        else:
                            if (
                                p_location == x
                                or
                                (
                                    l_mainfolder.id in ['countries', 'partners', 'publications']
                                    and
                                    x.meta_type == "Naaya Folder"
                                )
                                or
                                (
                                    l_mainfolder.id in ['documents']
                                    and
                                    x.meta_type == "Naaya URL"
                                    and x.id == 'thesaurus'
                                )
                            ): #coded for countries
                                buf = []
                                for y in childs:
                                    buf.append((y, 0))
                                if p_location == x:         #coded for countries
                                    l.append(((x, 1), buf))
                                else:
                                    l.append(((x, 0), buf))
                            else: l.append((x, 0))
                    return (l, l_mainfolder)
            else:
                #we are not inside a main topic, so don't show any left navigation
                return ([(x, 0) for x in self.getMainTopics()], None)

    security.declareProtected(view, 'admin_welcome_page')
    def admin_welcome_page(self, REQUEST=None):
        """ redirect to welcome page """
        username = REQUEST.AUTHENTICATED_USER.getUserName()
        profile = self.getProfilesTool().getProfile(username)
        sheet = profile.getSheetById(self.getInstanceSheetId())
        welcome_page = sheet.welcome_page
        page_ob = self.utGetObject(sheet.welcome_page)
        if page_ob == '' or page_ob is None:
            url_redirect = '%s' % (self.absolute_url())
        else:
            url_redirect = '%s/%s' % (self.absolute_url(), welcome_page)
        REQUEST.RESPONSE.redirect(url_redirect)

    def sendCreateAccountEmail(self, p_name, p_to, p_username,
                               REQUEST=None, **kwargs):
        #sends a confirmation email to the newlly created account's owner
        if REQUEST:
            kwargs.update(REQUEST.form)
        template = kwargs.get('p_template', 'email_createaccount')

        email_template = self.getEmailTool()._getOb(template)
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@EMAIL@@', kwargs.get('p_email', ''))
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        l_content = l_content.replace('@@ORGANISATION@@', '')
        l_content = l_content.replace('@@COMMENTS@@', '')
        l_content = l_content.replace('@@LOCATION@@', self.site_title)
        mail_from = self.mail_address_from
        self.getEmailTool().sendEmail(l_content, p_to, mail_from, l_subject)

    def sendAccountCreatedEmail(self, p_name, p_email, p_username, REQUEST, p_roles=[]):
        #sends a confirmation email to the newlly created account's owner
        if isinstance(p_roles, list): p_roles = ', '.join(p_roles)
        email_template = self.getEmailTool()._getOb('email_createaccount')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@EMAIL@@', p_email)
        l_content = l_content.replace('@@ROLES@@', p_roles)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        mail_from = self.mail_address_from
        self.getEmailTool().sendEmail(l_content, p_email, mail_from, l_subject)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSemideUsers')
    def getSemideUsers(self, query='', skey=0, rkey=''):
        """ return the portal users """
        site = self.getSite()
        if skey == 'user':  skey = 0
        elif skey == 'name':    skey = 1
        elif skey == 'email':   skey = 2
        else:   skey = 0
        users = []
        users_a = users.append
        for user in site.getAuthenticationTool().getUsers():
            if query:
                if self.utToUnicode(user.name).find(query)!=-1 or user.email.find(query)!=-1 or \
                   self.utToUnicode(user.firstname).find(query)!=-1 or self.utToUnicode(user.lastname).find(query)!=-1:
                    users_a((user.name, '%s %s' % (user.firstname, user.lastname), user.email, user.created, user.lastupdated, user.lastlogin, user.lastpost))
            else:
                users_a((user.name, '%s %s' % (user.firstname, user.lastname), user.email, user.created, user.lastupdated, user.lastlogin, user.lastpost))
        results = [(x[skey], x) for x in users]
        results.sort()
        if rkey: results.reverse()
        return [val for (key, val) in results]

    def getFilteredSemideUsers(self, query, limit=0):
        """ filter the user list """
        if query:
            users = self.getSemideUsers(query)
            if limit and len(users) > int(limit):
                return 0
            else:
                return users
        else:
            return []

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSemideUsersRoles')
    def getSemideUsersRoles(self):
        """ return the users with their roles """
        site = self.getSite()
        users = {}
        users_roles = site.getAuthenticationTool().getUsersRoles()
        for k, v in users_roles.items():
            if (len(v) > 1 and len(v[1][0]) > 0) or (len(v) == 1 and len(v[0][0]) > 0):
                users[k] = v
        return users

    #administration actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'handle_scheme_img_upload')
    def handle_scheme_img_upload(self, scheme, img, value):
        """
        Upload an image in the given colour scheme.
        """
        if value != '':
            if hasattr(value, 'filename'):
                if value.filename != '':
                    l_read = value.read()
                    if value != '':
                        ob = scheme._getOb(img)
                        ob.update_data(l_read)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'handle_scheme_css')
    def handle_scheme_css(self, style_src, marker_start, marker_end, value):
        """
        Upload an image in the given colour scheme.
        """
        if value != '':
            start = style_src.find(marker_start)
            end = style_src.find(marker_end)
            while start != -1:
                buf = style_src[0:start+len(marker_start)]
                buf = buf + value
                buf = buf + style_src[end:]
                style_src = buf
                start = style_src.find(marker_start, end)
                end = style_src.find(marker_end, start)
            return style_src
        return None

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_appearance')
    def admin_appearance(self, bckg_left='', bckg_left_ar='', bck_topmenu='',
                         topmenucolor='', bck_search='', bck_search_ar='', europe='', europe_ar='',
                         rightportletoutline='', entire_site_font='', entire_site_font_ar='', headings_font='', headings_font_ar='',
                         main_navigation_font='', main_navigation_font_ar='', left_second_font='', left_second_font_ar='', left_third_font='',
                         left_third_font_ar='', left_title_font='', left_title_font_ar='', left_title_color='', left_title_bg='',
                         left_title_border='', left_active_bg='', left_active_color='', left_active_size='', right_bg='', right_font='',
                         right_font_ar='', right_color='', right_size='', right_title_font='', right_title_font_ar='',
                         right_title_color='', right_title_size='',
                         bread_color='', bread_size='', bread_size_ar='', breadbar_bg='', search_bg='', quick_bg='',
                         quick_right_border='', search_left_border='', breadbar_middle_bg='', breadbar_middle_width='',
                         breadbar_upper_border='', breadbar_lower_border='',
                         search_bgimg=' ', search_bgimg_ar=' ', quick_bgimg=' ', quick_bgimg_ar=' ',
                         bg_search='', bg_search_ar='', bg_quickaccess='', bg_quickaccess_ar='',
                         breadbar_bgimg=' ', breadbar_bgimg_ar=' ',
                         REQUEST=None):
        """ WTF??? """
        scheme = self.getLayoutTool().getCurrentSkinScheme()
        style = scheme._getOb('style')
        style_src = style.document_src()
        buf = ''
        #upload images
        self.handle_scheme_img_upload(scheme, 'bckg_left.jpg', bckg_left)
        self.handle_scheme_img_upload(scheme, 'bckg_left_ar.jpg', bckg_left_ar)
        self.handle_scheme_img_upload(scheme, 'bck_search.jpg', bck_search)
        self.handle_scheme_img_upload(scheme, 'bck_search_ar.jpg', bck_search_ar)
        self.handle_scheme_img_upload(scheme, 'europe.jpg', europe)
        self.handle_scheme_img_upload(scheme, 'europe_ar.jpg', europe_ar)

        self.handle_scheme_img_upload(scheme, 'bg_search.gif', bg_search)
        self.handle_scheme_img_upload(scheme, 'bg_search_ar.gif', bg_search_ar)
        self.handle_scheme_img_upload(scheme, 'bg_quickaccess.gif', bg_quickaccess)
        self.handle_scheme_img_upload(scheme, 'bg_quickaccess_ar.gif', bg_quickaccess_ar)

        #modify CSS
        r = self.handle_scheme_css(style_src,
                                   MARKER_TOPMENUCOLOR_START,
                                   MARKER_TOPMENUCOLOR_END,
                                   topmenucolor)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHTPORTLETOUTLINE_START,
                                   MARKER_RIGHTPORTLETOUTLINE_END,
                                   rightportletoutline)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_ENTIRE_SITE_FONT_START,
                                   MARKER_ENTIRE_SITE_FONT_END,
                                   entire_site_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_ENTIRE_SITE_FONT_AR_START,
                                   MARKER_ENTIRE_SITE_FONT_AR_END,
                                   entire_site_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_HEADINGS_FONT_START,
                                   MARKER_HEADINGS_FONT_END,
                                   headings_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_HEADINGS_FONT_AR_START,
                                   MARKER_HEADINGS_FONT_AR_END,
                                   headings_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_MAIN_NAVIGATION_FONT_START,
                                   MARKER_MAIN_NAVIGATION_FONT_END,
                                   main_navigation_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_MAIN_NAVIGATION_FONT_AR_START,
                                   MARKER_MAIN_NAVIGATION_FONT_AR_END,
                                   main_navigation_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_SECOND_FONT_START,
                                   MARKER_LEFT_SECOND_FONT_END,
                                   left_second_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_SECOND_FONT_AR_START,
                                   MARKER_LEFT_SECOND_FONT_AR_END,
                                   left_second_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_THIRD_FONT_START,
                                   MARKER_LEFT_THIRD_FONT_END,
                                   left_third_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_THIRD_FONT_AR_START,
                                   MARKER_LEFT_THIRD_FONT_AR_END,
                                   left_third_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_TITLE_FONT_START,
                                   MARKER_LEFT_TITLE_FONT_END,
                                   left_title_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_TITLE_FONT_AR_START,
                                   MARKER_LEFT_TITLE_FONT_AR_END,
                                   left_title_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_TITLE_COLOR_START,
                                   MARKER_LEFT_TITLE_COLOR_END,
                                   left_title_color)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_TITLE_BG_START,
                                   MARKER_LEFT_TITLE_BG_END,
                                   left_title_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_TITLE_BORDER_START,
                                   MARKER_LEFT_TITLE_BORDER_END,
                                   left_title_border)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_ACTIVE_BG_START,
                                   MARKER_LEFT_ACTIVE_BG_END,
                                   left_active_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_ACTIVE_COLOR_START,
                                   MARKER_LEFT_ACTIVE_COLOR_END,
                                   left_active_color)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_LEFT_ACTIVE_SIZE_START,
                                   MARKER_LEFT_ACTIVE_SIZE_END,
                                   left_active_size)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_BG_START,
                                   MARKER_RIGHT_BG_END,
                                   right_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_FONT_START,
                                   MARKER_RIGHT_FONT_END,
                                   right_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_FONT_AR_START,
                                   MARKER_RIGHT_FONT_AR_END,
                                   right_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_COLOR_START,
                                   MARKER_RIGHT_COLOR_END,
                                   right_color)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_SIZE_START,
                                   MARKER_RIGHT_SIZE_END,
                                   right_size)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_TITLE_FONT_START,
                                   MARKER_RIGHT_TITLE_FONT_END,
                                   right_title_font)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_TITLE_FONT_AR_START,
                                   MARKER_RIGHT_TITLE_FONT_AR_END,
                                   right_title_font_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_TITLE_COLOR_START,
                                   MARKER_RIGHT_TITLE_COLOR_END,
                                   right_title_color)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_RIGHT_TITLE_SIZE_START,
                                   MARKER_RIGHT_TITLE_SIZE_END,
                                   right_title_size)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREAD_COLOR_START,
                                   MARKER_BREAD_COLOR_END,
                                   bread_color)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREAD_SIZE_START,
                                   MARKER_BREAD_SIZE_END,
                                   bread_size)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREAD_SIZE_AR_START,
                                   MARKER_BREAD_SIZE_AR_END,
                                   bread_size_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_BG_START,
                                   MARKER_BREADBAR_BG_END,
                                   breadbar_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_SEARCH_BG_START,
                                   MARKER_SEARCH_BG_END,
                                   search_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_QUICK_BG_START,
                                   MARKER_QUICK_BG_END,
                                   quick_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_QUICK_RIGHT_BORDER_START,
                                   MARKER_QUICK_RIGHT_BORDER_END,
                                   quick_right_border)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_SEARCH_LEFT_BORDER_START,
                                   MARKER_SEARCH_LEFT_BORDER_END,
                                   search_left_border)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_MIDDLE_BG_START,
                                   MARKER_BREADBAR_MIDDLE_BG_END,
                                   breadbar_middle_bg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_MIDDLE_WIDTH_START,
                                   MARKER_BREADBAR_MIDDLE_WIDTH_END,
                                   breadbar_middle_width)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_UPPER_BORDER_START,
                                   MARKER_BREADBAR_UPPER_BORDER_END,
                                   breadbar_upper_border)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_LOWER_BORDER_START,
                                   MARKER_BREADBAR_LOWER_BORDER_END,
                                   breadbar_lower_border)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_SEARCH_BGIMG_START,
                                   MARKER_SEARCH_BGIMG_END,
                                   search_bgimg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_SEARCH_BGIMG_AR_START,
                                   MARKER_SEARCH_BGIMG_AR_END,
                                   search_bgimg_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_QUICK_BGIMG_START,
                                   MARKER_QUICK_BGIMG_END,
                                   quick_bgimg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_QUICK_BGIMG_AR_START,
                                   MARKER_QUICK_BGIMG_AR_END,
                                   quick_bgimg_ar)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_BGIMG_START,
                                   MARKER_BREADBAR_BGIMG_END,
                                   breadbar_bgimg)
        if r is not None: style_src = r

        r = self.handle_scheme_css(style_src,
                                   MARKER_BREADBAR_BGIMG_AR_START,
                                   MARKER_BREADBAR_BGIMG_AR_END,
                                   breadbar_bgimg_ar)
        if r is not None: style_src = r
        style.pt_edit(text=style_src.encode('utf-8'), content_type='')
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_appearance_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'get_thumbs')
    def get_thumbs(self, thumb='', REQUEST=None):
        """ """
        return self.getThumbsFolder().objectValues('Image')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'add_thumb')
    def add_thumb(self, thumb='', REQUEST=None):
        """ """
        images_fld = self.getThumbsFolder()
        if thumb != '':
            if hasattr(thumb, 'filename'):
                if thumb.filename != '':
                    content = thumb.read()
                    if content != '':
                        img_id = 'thumb' + self.utGenRandomId(4)
                        images_fld.manage_addImage(id=img_id, title='', file='')
                        img_ob = images_fld._getOb(img_id)
                        img_ob.update_data(data=content)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_thumbnail_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'del_thumb')
    def del_thumb(self, ids='', REQUEST=None):
        """ """
        images_fld = self.getThumbsFolder()
        images_fld.manage_delObjects(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_thumbnail_html' % self.absolute_url())

    ############################################
    # Site map generation
    ############################################

    # Generic sitemap functions
    def getSiteMap(self, expand=[], root=None, showitems=0):
        #returns a list of objects with additional information
        #in order to draw the site map
        if root is None: root = self
        return self.__getSiteMap(root, showitems, expand, 0)

    def getSiteMapTrail(self, expand, tree):
        #given a list with all tree nodes, returns a string with all relatives urls
        if expand == 'all': return ','.join([node[0].absolute_url(1) for node in tree])
        else: return expand

    security.declarePublic('get_semide_containers_metatypes')
    def get_semide_containers_metatypes(self):
        """ this method is used to display local roles, called from getUserRoles methods """
        return [METATYPE_FOLDER, METATYPE_NYCOUNTRY]

    def __getSiteMap(self, root, showitems, expand, depth):
        #site map core
        l_tree = []
        l_folders = [x for x in root.objectValues(self.get_semide_containers_metatypes()) if x.approved == 1 and x.submitted==1]
        l_folders = self.utSortObjsListByAttr(l_folders, 'sortorder', 0)
        for l_folder in l_folders:
            if len(l_folder.objectValues(self.get_semide_containers_metatypes())) > 0 or (len(l_folder.getObjects()) > 0 and showitems==1):
                if l_folder.absolute_url(1) in expand or 'all' in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        buf = [x for x in l_folder.getPublishedObjects()]
                        for l_item in buf:
                            l_tree.append((l_item, -1, depth+1))
                    l_tree.extend(self.__getSiteMap(l_folder, showitems, expand, depth+1))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
        return l_tree

    # Remotechannels-specific sitemap functions
    def getSiteMapRemCh(self, expand=[], root=None, showitems=0):
        #returns a list of objects with additional information
        #in order to draw the site map
        if root is None: root = self
        return self.__getSiteMapRemCh(root, showitems, expand, 0)

    def test_containers_rc(self, p_container):
        #test if the given container contain News and/or Events
        meta_types = FolderMetaTypes(p_container).get_values()
        return (METATYPE_NYSEMNEWS in meta_types) or (METATYPE_NYSEMEVENT in meta_types)

    def __getSiteMapRemCh(self, root, showitems, expand, depth):
        #site map for Remotechannels
        l_tree = []
        l_folders = [x for x in root.objectValues(self.get_semide_containers_metatypes()) if x.approved == 1 and x.submitted==1]
        l_folders = self.utSortObjsListByAttr(l_folders, 'sortorder', 0)
        for l_folder in l_folders:
            if len(l_folder.objectValues(self.get_semide_containers_metatypes())) > 0 or (len(l_folder.getObjects()) > 0 and showitems==1):
                if l_folder.absolute_url(1) in expand or 'all' in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        buf = [x for x in l_folder.getPublishedObjects()]
                        for l_item in buf:
                            l_tree.append((l_item, -1, depth+1))
                    l_tree.extend(self.__getSiteMap(l_folder, showitems, expand, depth+1))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
        return l_tree

    # SEMIDE-specific sitemap functions
    def getSiteMapSEMIDE(self, expand=[], root=None, showitems=0):
        #returns a list of objects with additional information
        #in order to draw the site map
        if root is None: root = self
        return self.__getSiteMapSEMIDE(root, showitems, expand, 0, 4)

    def _get_non_folderish_objects(self, container):
        return [ obj for obj in container.objectValues() if obj.meta_type not in self.get_containers_metatypes() ]

    def __getSiteMapSEMIDE(self, root, showitems, expand, depth, maxdepth):
        #custom function for the SEMIDE websites
        #has specific expanded nodes
        l_maintopics = self.getMainTopics()
        l_tree = []
        if root is self:
            l_folders = [x for x in root.objectValues(self.get_semide_containers_metatypes()) if x.approved == 1 and x.submitted==1 and x in l_maintopics]
        else:
            l_folders = root.getPublishedFolders()
            l_folders.extend(root.objectValues(METATYPE_NYCOUNTRY))
        l_folders = self.utSortObjsListByAttr(l_folders, 'sortorder', 0)
        for l_folder in l_folders:
            if ((len(l_folder.objectValues(self.get_semide_containers_metatypes())) > 0) or ((len(l_folder.getObjects()) > 0) and showitems==1) or (l_folder.id=='about' and self is root)):
                if l_folder.absolute_url(1) in expand or 'all' in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        buf = [x for x in l_folder.getPublishedObjects() if x.meta_type != METATYPE_NYCOUNTRY]
                        for l_item in buf:
                            l_tree.append((l_item, -1, depth+1))
                    l_tree.extend(self.__getSiteMapSEMIDE(l_folder, showitems, expand, depth+1, maxdepth))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
            if ((root is self) and (l_folder.id=='about') and (l_folder.absolute_url(1) in expand or 'all' in expand)):
                for element in self.utSortObjsListByAttr(self._get_non_folderish_objects(l_folder),'sortorder',0):
                    l_tree.append((element, -1, 1))
        return l_tree

    ############################################
    # Search
    ############################################

    def setResTrans(self, res, lang, trans):
        """ """
        if res[lang]:
            res[lang] += ' or %s' % trans
        else:
            res[lang] = trans

    def translateQuery(self, query, search_languages):
        """ """
        utStrip = self.utStripString
        provider = self.getPortalThesaurus()
        curr_lang = self.gl_get_selected_language()
        res = {}
        #set the default result structure
        for k in search_languages:
            res[k] = ''

        #search associated translations from thesaurus
        for v in self.splitToList(query, ' or '):
            for l_lang in search_languages:
                th_term = provider.searchThesaurusNames(query=v, lang=l_lang)

                #search for the exact match
                exact_term = None
                for k in th_term:
                    l_term = provider.getTermByID(k.concept_id, l_lang)
                    if utStrip(l_term.concept_name) == utStrip(v):
                        exact_term = l_term
                        break
                if exact_term:
                    break

            #get the translations of the exact match
            if exact_term:
                for l_lang in search_languages:
                    l_term = provider.getTermByID(exact_term.concept_id, l_lang)
                    if l_term:
                        trans = l_term.concept_name
                        self.setResTrans(res, l_lang, trans)
                    else:
                        self.setResTrans(res, l_lang, v)
            else:
                for l_lang in search_languages:
                    self.setResTrans(res, l_lang, v)

        return res

    security.declareProtected(view, 'simpleSearch')
    def simpleSearch(self, query='', skey='', rkey=0, page_search_start='', search_languages=[], obj_types='', sreleased='', sreleased_when='0', where='all'):
        """ Default search method
        """
        try: page_search_start = int(page_search_start)
        except: page_search_start = 0
        if query:
            if where == 'all': path = ''
            else: path = where
            if type(query) == type(''):
                query = self.utStrEscapeForSearch(query)
            results = []
            l_query = 'self.getCatalogedObjects(approved=1, path=path'
            if obj_types != '':
                l_query += ', meta_type=%s' % obj_types
            try: l_released = self.utConvertStringToDateTimeObj(sreleased)
            except: l_released = ''
            if l_released:
                if sreleased_when == '1':
                    l_query += ', releasedate=l_released, releasedate_range=\'min\''
                else:
                    l_query += ', releasedate=l_released, releasedate_range=\'max\''
            try:
                trans_query = self.translateQuery(query, search_languages)
                for lang in search_languages:
                    l_expr = l_query
                    if query: l_expr += ', objectkeywords_%s=trans_query[\'%s\']' % (lang, lang)
                    l_expr += ')'
                    results.extend(eval(l_expr))
                l_query += ', PrincipiaSearchSource=query)'
                results.extend(eval(l_query))
            except:
                results = []
            results = self.utEliminateDuplicatesByURL(results)
            res = [r for r in results if r.can_be_seen()]

            batch_obj = batch_utils(self.numberresultsperpage, len(res), page_search_start)
            if skey != '':
                res = self.utSortObjsListByAttr(res, skey, rkey)
            if len(res) > 0:
                paging_informations = batch_obj.butGetPagingInformations()
            else:
                paging_informations = (-1, 0, 0, -1, -1, 0, self.numberresultsperpage, [0])
            return (paging_informations, res[paging_informations[0]:paging_informations[1]])
        else:
            return []

    security.declareProtected(view, 'search_advanced_html')
    def search_advanced_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_search_advanced')

    security.declareProtected(view, 'search_google_html')
    def search_google_html(self, REQUEST=None, RESPONSE=None):
        """ Google search widget """
        return self.getFormsTool().getContent({'here': self}, 'site_search_google')

    security.declareProtected(view, 'getSearchableMetaTypes')
    def getSearchableMetaTypes(self):
        """ Returns all installed meta types that should be searched
        """
        r = []
        ra = r.append
        pc = self.get_pluggable_content()
        seachable_metas = [x for x in self.get_pluggable_installed_meta_types() if x not in [METATYPE_NYSEMFIELDSITE, METATYPE_NYSEMFUNDING, METATYPE_NYSEMORGANISATION]]
        for k in seachable_metas:
            ra((k, pc[k]['label']))
        ra((METATYPE_FOLDER, 'Folder'))
        return r

    #quick access related
    security.declareProtected(view, 'getQuickAccess')
    def getQuickAccess(self, qa_url='', REQUEST=None):
        """ """
        if not qa_url: qa_url = self.getSitePath()
        if REQUEST: REQUEST.RESPONSE.redirect('%s' % qa_url)

    #list of links
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'testProtectedLinkList')
    def testProtectedLinkList(self, id=''):
        """ test if a list of links should be undeletable """
        if id in ['menunav_links', 'footer_links', 'quick_access']:
            return 1
        return 0

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_thumbnail_html')
    def admin_thumbnail_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_thumbnail')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flash_settings_html')
    def admin_flash_settings_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_flash_settings')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flash_notification_html')
    def admin_flash_notification_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_flash_notification')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashusers_html')
    def admin_flashusers_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_flashusers')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashhtml_html')
    def admin_flashhtml_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_flashhtml')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashtext_html')
    def admin_flashtext_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_flashtext')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_appearance_html')
    def admin_appearance_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_appearance')

    security.declareProtected(view, 'site_admin_remotechannels_sitemap_html')
    def site_admin_remotechannels_sitemap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_remotechannels_sitemap')

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flash_settings')
    def admin_flash_settings(self, title='', path='', archive_path='', news_sd='', news_ed='', event_sd='', event_ed='', doc_sd='',
                             doc_ed='', notif_date='', notif_admin='', uploadmetatypes=[], lang=[], REQUEST=None):
        """ edit eflash """
        flash_tool = self.getFlashTool()
        flash_tool.manageSettings(title, path, archive_path, news_sd, news_ed, event_sd, event_ed, doc_sd, doc_ed,
                                  notif_date, notif_admin, uploadmetatypes, lang)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('admin_flash_settings_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flash_generate')
    def admin_flash_generate(self, REQUEST=None):
        """ """
        flashtool_ob = self.getFlashTool()
        flag = flashtool_ob.generate_flash()
        if flag:
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_GENERATED)
                REQUEST.RESPONSE.redirect('%s/admin_flashhtml_html' % self.absolute_url())
        else:
            if REQUEST:
                REQUEST.RESPONSE.redirect('%s/admin_flashhtml_html?empty=1' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashhtml_save')
    def admin_flashhtml_save(self, body='', lang=None, REQUEST=None):
        """ """
        flashtool_ob = self.getFlashTool()
        doc_ob = flashtool_ob.getFlashDocument('html')
        doc_ob.saveProperties(title='Flash to be sent on %s (html version)' % self.utShowDateTime(flashtool_ob.notif_date), body=body, lang=lang)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_flashhtml_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashtext_save')
    def admin_flashtext_save(self, body='', lang=None, REQUEST=None):
        """ """
        flashtool_ob = self.getFlashTool()
        doc_ob = flashtool_ob.getFlashDocument('text')
        doc_ob.saveProperties(title='Flash to be sent on %s (text version)' % self.utShowDateTime(flashtool_ob.notif_date), body=body, lang=lang)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_flashtext_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashemail')
    def admin_flashemail(self, subject='', body='', REQUEST=None):
        """ """
        self.getFlashTool().emailUsers(subject, body)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_EMAILSENT)
            REQUEST.RESPONSE.redirect('%s/admin_flashusers_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_flashexportusers')
    def admin_flashexportusers(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFlashTool().exportFlashUsers(REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_exportusers')
    def admin_exportusers(self, REQUEST=None, RESPONSE=None):
        """ """
        data = [('Username', 'Name', 'Email', 'Created', 'Updated', 'Last login', 'Last activity')]
        data_app = data.append
        for user in self.getSemideUsers():
            data_app((user[0], self.utToUtf8(user[1]), user[2], user[3], user[4], user[5], user[6]))
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % 'portalusers.csv')
        return content

    #update scripts
    security.declareProtected(view_management_screens, 'update_countries_1')
    def update_countries_1(self):
        """ """
        from Products.NaayaCore.PortletsTool.HTMLPortlet import addHTMLPortlet
        for x in self.countries.objectValues(METATYPE_NYCOUNTRY):
            addHTMLPortlet(x, id=x.get_portlet_indicators_id(),
                           title='Key indicators', lang='en')
            addHTMLPortlet(x, id=x.get_portlet_reports_id(),
                           title='Important reports', lang='en')

    security.declareProtected(view_management_screens, 'update_documents')
    def update_documents(self, REQUEST=None):
        """ """
        from Products.Naaya.managers.skel_parser import skel_parser
        #add new indexes in the Catalog
        try:    self.getCatalogTool().addIndex('resource_type', 'FieldIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('geozone', 'FieldIndex')
        except: pass
        try:    self.getCatalogTool().addIndex('statute', 'FieldIndex')
        except: pass

        #update the reflists
        portletstool_ob = self.getPortletsTool()
        skel_handler, error = skel_parser().parse(self.futRead(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'skel.xml'), 'r'))
        if skel_handler is not None:
            for reflist in skel_handler.root.portlets.reflists:
                reflist_ob = portletstool_ob._getOb(reflist.id, None)
                if reflist_ob is None:
                    portletstool_ob.manage_addRefList(reflist.id, reflist.title, reflist.description)
                    reflist_ob = portletstool_ob._getOb(reflist.id)
                else:
                    reflist_ob.manage_delete_items(reflist_ob.get_collection().keys())
                for item in reflist.items:
                    reflist_ob.add_item(item.id, item.title)
        #update subobjects list
        documents_obj = self._getOb('documents')
        ny_subobjects = [METATYPE_FOLDER,METATYPE_NYSEMEVENT,METATYPE_NYSEMNEWS,METATYPE_NYDOCUMENT, \
                         METATYPE_NYFILE, METATYPE_NYURL,METATYPE_NYPOINTER,METATYPE_NYSEMMULTIMEDIA, METATYPE_NYSEMTEXTLAWS, \
                         METATYPE_NYSEMDOCUMENT]
        meta_types = FolderMetaTypes(documents_obj)
        ny_subobjects.extend(meta_types.get_values())
        meta_types.set_values(list(set(ny_subobjects)))


    #Initiatives Folder has 2 portlets (News & Events) present in every header of its subfolders.
    def get_initiatives_portlets_objects(self):
        #the Events and News Portlets for Initiatives SubFolders
        l = []
        p = self.getPortletsTool()._getOb('portlet_initiatives_news', None)
        if p is not None: l.append(p)
        p = self.getPortletsTool()._getOb('portlet_initiatives_events', None)
        if p is not None: l.append(p)
        p = self.getPortletsTool()._getOb('portlet_initiatives_projects', None)
        if p is not None: l.append(p)
        return l

    def getInitiativesList(self, context, type='news', lang=None):
        """ Get a list of news, events or projects related to the current folder by keywords or title """
        if type == 'news':
            meta_type = METATYPE_NYSEMNEWS
        elif type == 'events':
            meta_type = METATYPE_NYSEMEVENT
        elif type == 'projects':
            meta_type = METATYPE_NYSEMPROJECT

        if not lang: lang = self.gl_get_selected_language()

        search_keywords = u' or '.join((context.getLocalProperty('keywords', lang) + ' ' + context.getLocalProperty('title', lang)).split())
        objectkeywords = 'objectkeywords_' + lang
        return self.getCatalogedObjects(meta_type=meta_type, approved=1, howmany=5, **{objectkeywords: search_keywords})

    #ProfileMeta implementation
    security.declarePrivate('loadProfileMeta')
    def loadProfileMeta(self):
        """
        Load profile metadata and updates existing profiles.
        """
        self._loadProfileMeta(os.path.join(SEMIDE_PRODUCT_PATH, 'skel', 'others'))

    security.declareProtected(view, 'profilesheet')
    def profilesheet(self, name=None, welcome_page='', REQUEST=None):
        """
        Updates the profile of the given user. Must be implemented.
        """
        if name is None: name = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._profilesheet(name, {'welcome_page': welcome_page})
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/profilesheet_html' % self.absolute_url())

    security.declareProtected(view, 'profilesheet_html')
    def profilesheet_html(self, REQUEST=None, RESPONSE=None):
        """
        View for instance associated sheet. Must be implemented.
        """
        return self.getFormsTool().getContent({'here': self}, 'site_profilesheet')

    def get_oai_aggregators(self):
        """ """
        return self.objectValues(OAIAggregator.OAIAggregator.meta_type)

    def get_oai_servers(self):
        """ returns the list of ZoPe OAI servers """
        return self.objectValues(OAIServer.OAIServer.meta_type)

    security.declarePublic('oai_trigger')
    def oai_trigger(self, uid):
        """
        Used by cron tools to trigger the OAI Server update.

        @param uid: site uid
        @type uid: string
        """
        if uid==self.get_site_uid():
            for server in self.get_oai_servers():
                server.update()

    security.declarePublic('agregator_trigger')
    def agregator_trigger(self, uid):
        """
        Used by cron tools to the OAI agregator update.

        @param uid: site uid
        @type uid: string
        """
        if uid==self.get_site_uid():
            for oai_aggregator in self.get_oai_aggregators():
                oai_aggregator.update()

    #highlight searched words
    def getHighlightWordsInText(self, p_text, p_words="", p_highlight_start="<span class='hlighted'>",
                                p_highlight_end="</span>", p_phrases = 3, p_nosplit = False):
        return semide_utils.html_utils().highlightWordsInText(p_text, p_words, p_highlight_start, p_highlight_end, p_phrases, p_nosplit)

    def getHighlightWordsInHtml(self, p_text, p_words="", p_highlight_start="<span class='hlighted'>",
                                p_highlight_end="</span>", p_phrases = 3, p_nosplit = False):
        return semide_utils.html_utils().highlightWordsInHtml(p_text, p_words, p_highlight_start, p_highlight_end, p_phrases, p_nosplit)

    #site pages
    security.declareProtected(view, 'insertrelativelink_html')
    def insertrelativelink_html(self, REQUEST=None, RESPONSE=None):
        """
        Opens a page with site map and insert a relative link in the wysiwyg widget editor.
        """
        return self.getFormsTool().getContent({'here': self}, 'site_insertrelativelink')

    #download ZIP
    security.declarePrivate('getDownloadContext')
    def getDownloadContext(self, p_url):
        """ """
        return self.unrestrictedTraverse(p_url)

    security.declarePublic('get_downloadable_metatypes')
    def get_downloadable_metatypes(self):
        #this method is used to return downloadables types
        return [METATYPE_FOLDER, METATYPE_NYFILE, METATYPE_NYEXFILE, METATYPE_NYPHOTO]

    def get_ziped_metatypes(self):
        #this method is used to return downloadables types
        return [METATYPE_NYFILE, METATYPE_NYEXFILE, METATYPE_NYPHOTO]

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'nfp_download_html')
    def nfp_download_html(self, fld_url, REQUEST=None, RESPONSE=None):
        """ """
        obj_container = self.getDownloadContext(fld_url)
        return self.getFormsTool().getContent({'here': obj_container}, 'nfp_download')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'downloadObjects')
    def downloadObjects(self, REQUEST=None):
        """ downloads objects """
        l_id_list = self.utConvertToList(REQUEST.get('id', []))
        fld_url = REQUEST.get('fld_url', '')
        l_list = self.utJoinToString(l_id_list)
        if REQUEST: REQUEST.RESPONSE.redirect('nfp_download_html?files=%s&fld_url=%s' % (l_list, fld_url))

    security.declareProtected(view, 'testNFPContext')
    def testNFPContext(self, l_url):
        """ """
        l_context = self.splitToList(l_url, '/')
        if 'nfp_private' in l_context and 'download' in l_context:
            return True
        return False

    def getDownloadInformation(self, p_ids, fld_url):
        #returns download information
        l_context = self.getDownloadContext(fld_url)
        l_folders = 0
        l_files = 0
        for k in p_ids:
            l_ob = l_context.getObjectById(k)
            if l_ob.meta_type in self.get_containers_metatypes():
                l_folders += 1
            if l_ob.meta_type in self.get_ziped_metatypes():
                l_files += 1
        return (l_folders, l_files)

    def countObjectsFolder(self, p_obj):
        #return the number of objects inside the container
        l_results = 0
        l_objects = p_obj.objectValues(self.get_downloadable_metatypes())
        for l_ob in l_objects:
            if l_ob.meta_type in self.get_ziped_metatypes(): l_results += 1
            else:
                l_all_childs = 0
                l_all_childs = self.countObjectsFolder(l_ob)
                l_results = l_results + l_all_childs
        return l_results

    def getSizeForObj(self, p_ob):
        #transforms a file size in Kb, Mb ..
        p_size = p_ob.get_size()
        return self.getSize(p_size)

    def getSize(self, p_float = 0):
        #transforms a size in Kb, Mb ..
        l_bytes = float(p_float)
        l_type = ''
        if l_bytes >= 1000:
            l_bytes = l_bytes/1024
            l_type = 'Kb'
            if l_bytes >= 1000:
                l_bytes = l_bytes/1024
                l_type = 'Mb'
            l_res = '%s %s' % ('%4.2f' % l_bytes, l_type)
        else:
            l_type = 'Bytes'
            l_res = '%s %s' % ('%4.0f' % l_bytes, l_type)
        return l_res

    #country
    security.declarePublic('testCountryContext')
    def testCountryContext(self, context):
        """ """
        return context.meta_type == METATYPE_NYCOUNTRY

    #update river basin from Glossary
    security.declarePrivate('updateRBFromGlossary')
    def updateRBFromGlossary(self, sem_ob, lang):
        """
        Update the river basin property from the associated
        glossary for each language other than the current one.
        """
        lang_name = self.gl_get_language_name(lang)
        provider_rb = self._getOb(ID_GLOSSARY_RIVER_BASIN)
        if provider_rb:
            self.__updateRBFromGlossary(sem_ob, provider_rb, 'fieldsite_rb', lang, lang_name)

    def __updateRBFromGlossary(self, sem_ob, provider, prop, lang_code, lang_name):
        #update river basin from glossary
        utStrip = self.utStripString
        langs = self.gl_get_languages_mapping()
        res = {}

        #creates the results dictionary
        for l in langs:
            if l['name'] != lang_name:
                res[l['code']] = ''

        #search associated translations from glossary
        if provider.meta_type == NAAYAGLOSSARY_CENTRE_METATYPE:
            for v in self.splitToList(sem_ob.getLocalProperty(prop, lang_code)):
                gloss_elems = provider.searchGlossary(query=v, language=lang_name, definition='')

                #search for the exact match
                exact_elem = None
                for l_elem in gloss_elems[2]:
                    l_trans = l_elem.get_translation_by_language(lang_name)
                    if utStrip(l_trans) == utStrip(v):
                        exact_elem = l_elem
                        break

                #get the translations of the exact match
                if exact_elem:
                    for l in langs:
                        l_code = l['code']
                        l_name = l['name']
                        if l_name != lang_name:
                            trans = exact_elem.get_translation_by_language(l_name)
                            if res[l_code] and trans:        res[l_code] = '%s, %s' % (res[l_code], trans)
                            elif not res[l_code] and trans:  res[l_code] = trans

        #set values
        for k in res.keys():
            trans = self.utToUnicode(res[k])
            if trans: sem_ob._setLocalPropValue(prop, k, trans)

    security.declarePublic('changeLangAndRedirect')
    def changeLangAndRedirect(self, lang='', url='', REQUEST=None):
        """ """
        # Code compatible with both Localizer (old) and naaya.i18n (new)
        try:
            portal_i18n = portal.getPortalI18n()
            portal_i18n.change_selected_language(lang)
        except AttributeError:
            self.getLocalizer().changeLanguage(lang)

        if REQUEST:
            REQUEST.RESPONSE.redirect(url)

    security.declarePublic('stripAllHtmlTags')
    def stripAllHtmlTags(self, p_text):
        """ """
        return semide_utils.html_utils().stripAllHtmlTags(p_text)

    #Link checker relatd
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_link_checker_html')
    def admin_link_checker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkchecker')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'folder_linkchecker_html')
    def folder_linkchecker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_linkchecker')

    #latest comments
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_latest_comments_html')
    def admin_latest_comments_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_comments')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'get_latest_comments')
    def get_latest_comments(self):
        """ """
        return self.getCatalogTool().getLatestComments(path='/', limit=20)

    security.declareProtected(view, 'search_rdf')
    # XXX Use decorators in python 2.4+
    # @content_type_xml
    # @cachable
    def search_rdf(self, REQUEST=None, **kwargs):
        """ """
        search_mapping = RDF_SEARCH_MAPPING
        search_query_mapping = RDF_SEARCH_QUERY_MAPPING

        site = self.getSite()
        if REQUEST.form:
            form = dict(REQUEST.form)
        else:
            form = dict(kwargs)

        search_by = form.get('search_by', '')
        search_method = search_mapping.get(search_by, None)
        search_method = search_method and getattr(site, search_method, None)
        if not search_method:
            logger.warn(('SEMIDESite.search_rdf'
                         'Unknown search_by: %s => search_method: %s'),
                        search_by, search_method)
            return self.getSyndicationTool().syndicateSomething(
                self.absolute_url(), [])

        # XXX Ugly hack
        for key, value in search_query_mapping.items():
            req_value = form.get(key, None)
            if not req_value:
                continue
            form.setdefault(value, req_value)

        try:
            results = search_method(**form)
        except TypeError, err:
            logger.exception(err)
            return self.getSyndicationTool().syndicateSomething(
                self.absolute_url(), [])

        objects = [x.getObject() for x in results[
            int(form.get('ps_start', 0)):int(form.get('items', 10))]]

        return self.getSyndicationTool().syndicateSomething(
            self.absolute_url(), objects)
    search_rdf = content_type_xml(cachable(search_rdf))

    security.declareProtected(view, 'search_atom')
    # XXX Use decorators in python 2.4+
    # @content_type_xml
    # @cachable
    def search_atom(self, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        search_mapping = RDF_SEARCH_MAPPING
        search_query_mapping = RDF_SEARCH_QUERY_MAPPING

        site = self.getSite()
        form = REQUEST.form
        search_by = form.get('search_by', '')
        search_method = search_mapping.get(search_by, None)
        search_method = search_method and getattr(site, search_method, None)
        if not search_method:
            logger.exception('Unknown search_by: %s => search_method: %s',
                             search_by, search_method)
            return self.getSyndicationTool().syndicateAtom(self, [])

        # XXX Ugly hack
        for key, value in search_query_mapping.items():
            req_value = form.get(key, None)
            if not req_value:
                continue
            form.setdefault(value, req_value)
        try:
            results = search_method(**form)
        except TypeError, err:
            logger.exception(err)
            return self.getSyndicationTool().syndicateAtom(self, [])

        # See getNewsListing or similar search methods
        objects = [x.getObject() for x in results[
            int(form.get('ps_start', 0)):int(form.get('items', 10))]]
        return self.getSyndicationTool().syndicateAtom(self, objects)
    search_atom = content_type_xml(cachable(search_atom))

    # Customize Naaya switchToLanguage in order to handle Semide content types
    security.declarePrivate('_getCustomSwitchToLangDenyArgs')
    def _getCustomSwitchToLangDenyArgs(self, meta_type="", deny_args=[]):
        """ Handle custom semide content types
        """
        if meta_type in ('Naaya Semide Event', 'Naaya Semide Document',
                         'Naaya Semide Multimedia', 'Naaya Semide News',
                         'Naaya Semide Text of Laws',
                         ):
            deny_args = tuple([x for x in deny_args if x != 'source'])
        return deny_args

InitializeClass(SEMIDESite)

class DummyComment:
    """ """

    def __init__(self, comm_parent, comm_ob, comm_date):
        self.comm_parent =  comm_parent
        self.comm_ob =      comm_ob
        self.comm_date =    comm_date

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(DummyComment)
