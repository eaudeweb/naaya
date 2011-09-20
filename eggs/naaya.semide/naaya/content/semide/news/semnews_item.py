import os
import sys
from copy import deepcopy
from Acquisition import Implicit
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile
from OFS.Image import cookId
import zope.event

from naaya.content.base.constants import MUST_BE_NONEMPTY, MUST_BE_POSITIV_INT, MUST_BE_DATETIME
from Products.NaayaBase.constants import (PERMISSION_EDIT_OBJECTS, EXCEPTION_NOTAUTHORIZED,
EXCEPTION_NOTAUTHORIZED_MSG, EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG,
EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG, MESSAGE_SAVEDCHANGES)

from Products.NaayaCore.managers.utils import make_id, get_nsmap
from naaya.i18n.LocalPropertyManager import LocalProperty

from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.Naaya.adapters import FolderMetaTypes

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core import submitter

from lxml import etree
from lxml.builder import ElementMaker

#Module constants
METATYPE_OBJECT = 'Naaya Semide News'
LABEL_OBJECT = 'News'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide News objects'
OBJECT_FORMS = ['semnews_add', 'semnews_edit', 'semnews_index']
OBJECT_CONSTRUCTORS = ['manage_addNySemNews_html', 'semnews_add_html', 'addNySemNews', 'importNySemNews']
OBJECT_ADD_FORM = 'semnews_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide News type.'
PREFIX_OBJECT = 'snews'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (1, MUST_BE_NONEMPTY, 'The Geographical coverage field must have a value.'),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'creator':          (0, '', ''),
    'creator_email':    (0, '', ''),
    'contact_person':   (0, '', ''),
    'contact_email':    (0, '', ''),
    'contact_phone':    (0, '', ''),
    'news_type':        (0, '', ''),
    'file_link':        (0, '', ''),
    'file_link_local':  (0, '', ''),
    'source':           (0, '', ''),
    'source_link':      (0, '', ''),
    'subject':          (0, '', ''),
    'relation':         (0, '', ''),
    'news_date':        (0, '', ''),
    'working_langs':    (0, '', ''),
    'lang':             (0, '', ''),
    'file':             (0, '', ''),
}

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'news_date':        dict(sortorder=100, widget_type="Date", data_type="date", label="News date"),
    'source':           dict(sortorder=110, widget_type="String", label="Source", localized=True),
    'source_link':      dict(sortorder=120, widget_type="String", label="Source link", default="http://"),
    'news_type':        dict(sortorder=130, widget_type="Select", label="News type", list_id="news_types"),
    'subject':          dict(sortorder=150, widget_type="SelectMultiple", label="Subject", localized=True),
    'creator':          dict(sortorder=160, widget_type="String", label="Creator", localized = True, visible=False, default=''),
    'creator_email':    dict(sortorder=170, widget_type="String", label="Creator e-mail", visible=False, default=''),
    'contact_person':   dict(sortorder=180, widget_type="String", label="Contact name", localized=True),
    'contact_email':    dict(sortorder=190, widget_type="String", label="Contact e-mail", localized=True),
    'contact_phone':    dict(sortorder=200, widget_type="String", label="Contact phone", localized=True),
    'working_langs':    dict(sortorder=210, widget_type="SelectMultiple", label="Working langs"),
    'relation':         dict(sortorder=220, widget_type="String", label="Relation"),
    'file_link':        dict(sortorder=240, widget_type="String", label="Full description link", localized=True, default="http://"),

})
DEFAULT_SCHEMA['sortorder'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)

config = {
        'product': 'NaayaContent',
        'module': 'NySemNews',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'properties': PROPERTIES_OBJECT,
        'schema_name': 'NySemNews',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySemNews.gif'),
        '_misc': {
                'NySemNews.gif': ImageFile('www/NySemNews.gif', globals()),
                'NySemNews_marked.gif': ImageFile('www/NySemNews_marked.gif', globals()),
            },
    }

manage_addNySemNews_html = PageTemplateFile('zpt/semnews_manage_add', globals())
manage_addNySemNews_html.kind = METATYPE_OBJECT
manage_addNySemNews_html.action = 'addNySemNews'

def semnews_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self,
                                           'kind': METATYPE_OBJECT,
                                           'action': 'addNySemNews',
                                           'form_helper': form_helper
                                           }, 'semnews_add')

def _create_NySemNews_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NySemNews(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def create_month_folder(self, contributor, schema_raw_data):
    #Creating archive folder
    news_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('news_date', None))
    news_date_year = str(news_date.year())
    news_date_month = news_date.mm()

    year_folder = self._getOb(news_date_year, None)
    if year_folder is None:
        year_folder = self._getOb(addNyFolder(self, news_date_year,
            contributor=contributor, title="News for %s" % news_date_year))

    month_folder = year_folder._getOb(news_date_month, None)
    if month_folder is None:
        month_folder = year_folder._getOb(addNyFolder(year_folder, news_date_month,
                        contributor=contributor,
                        title="News for %s/%s" %
                        (news_date_year, news_date_month)))
    FolderMetaTypes(month_folder).add(config['meta_type'])
    return month_folder

def addNySemNews(self, id='', contributor=None, REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    #process parameters
    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix=PREFIX_OBJECT)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    if schema_raw_data.get('archive'):
        try:
            month_folder = create_month_folder(self, contributor, schema_raw_data)
        except:
            month_folder = self
    else:
        month_folder = self
    ob = _create_NySemNews_object(month_folder, id, contributor)
    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    ob.news_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('news_date', None))

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/semnews_add_html' % self.absolute_url())


    if 'file' in schema_raw_data:
        ob.handleUpload(schema_raw_data['file'])

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()
    ob.updatePropertiesFromGlossary(_lang)

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    zope.event.notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))

    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'semnews_manage_add' or l_referer.find('semnews_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif 'semnews_add_html' in l_referer:
            self.setSession('referer', self.absolute_url())
            response = ob.object_submitted_message(REQUEST)
            if schema_raw_data.get('archive'):
                response = REQUEST.RESPONSE.redirect(self.absolute_url())
            return response
    return ob.getId()

def importNySemNews(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param == 3:
        #just try to delete the object
        try: self.manage_delObjects([id])
        except: pass
    else:
        ob = self._getOb(id, None)
        if param in [0, 1] or (param==2 and ob is None):
            if param == 1:
                #delete the object if exists
                try: self.manage_delObjects([id])
                except: pass
            #Creating object and setting all object properties (taken from Schema)
            ob = _create_NySemNews_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            for prop in ob._get_schema().listPropNames():
                setattr(ob, prop, '')
            for k, v  in attrs.items():
                setattr(ob, k, v.encode('utf-8'))

            if objects:
                obj = objects[0]
                data=self.utBase64Decode(obj.attrs['file'].encode('utf-8'))
                ctype = obj.attrs['content_type'].encode('utf-8')
                try:
                    size = int(obj.attrs['size'])
                except (TypeError, ValueError):
                    size = 0
                name = obj.attrs['name'].encode('utf-8')
                ob.update_data(data, ctype, size, name)
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class semnews_item(Implicit, NyContentData, NyFSContainer):
    """ """
    meta_type = METATYPE_OBJECT
    file_link_local =   LocalProperty('file_link_local')

class NySemNews(semnews_item, NyAttributes, NyItem, NyCheckControl, NyContentType, NyValidation):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemNews.gif'
    icon_marked = 'misc_/NaayaContent/NySemNews_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        semnews_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'resource_type')
    def resource_type(self):
        return getattr(self, 'news_type', None)

    security.declareProtected(view, 'resource_date')
    def resource_date(self):
        return getattr(self, 'news_date', None)

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
            return ' '.join(getattr(self, 'subject', []))

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('source', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'creator="%s" creator_email="%s" news_type="%s" \
                source_link="%s" subject="%s" relation="%s" news_date="%s" working_langs="%s"' % \
            (self.utXmlEncode(self.creator),
                self.utXmlEncode(self.creator_email),
                self.utXmlEncode(self.news_type),
                self.utXmlEncode(self.source_link),
                self.utXmlEncode(self.subject),
                self.utXmlEncode(self.relation),
                self.utXmlEncode(self.news_date),
                self.utXmlEncode(self.working_langs))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<contact_person lang="%s"><![CDATA[%s]]></contact_person>' % (l, self.utToUtf8(self.getLocalProperty('contact_person', l))))
            ra('<contact_email lang="%s"><![CDATA[%s]]></contact_email>' % (l, self.utToUtf8(self.getLocalProperty('contact_email', l))))
            ra('<contact_phone lang="%s"><![CDATA[%s]]></contact_phone>' % (l, self.utToUtf8(self.getLocalProperty('contact_phone', l))))
            ra('<rights lang="%s"><![CDATA[%s]]></rights>' % (l, self.utToUtf8(self.getLocalProperty('rights', l))))
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
            ra('<file_link lang="%s"><![CDATA[%s]]></file_link>' % (l, self.utToUtf8(self.getLocalProperty('file_link', l))))
            ra('<file_link_local lang="%s"><![CDATA[%s]]></file_link_local>' % (l, self.utToUtf8(self.getLocalProperty('file_link_local', l))))
        if self.getSize():
            ra('<item file="%s" content_type="%s" size="%s" name="%s"/>' % (
                self.utBase64Encode(str(self.utNoneToEmpty(self.get_data()))),
                self.utXmlEncode(self.utToUtf8(self.getContentType())),
                self.utToUtf8(self.getSize()),
                self.utToUtf8(self.downloadfilename()))
        )
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        item = rss_item_for_object(self, lang)
        nsmap = get_nsmap(self.getSyndicationTool().getNamespaceItemsList())
        Dc = ElementMaker(namespace=nsmap['dc'], nsmap=nsmap)
        Ut = ElementMaker(namespace=nsmap['ut'], nsmap=nsmap)
        item.extend(Dc.root(
            Dc.type('Text'),
            Dc.format(self.format()),
            Dc.source(self.getLocalProperty('source', lang)),
            Dc.creator(self.getLocalProperty('creator', lang)),
            Dc.publisher(self.getLocalProperty('publisher', lang)),
            Dc.relation(self.relation)
            ))
        for k in self.subject:
            if k:
                theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
                theme_name = theme_ob.theme_name
                if theme_name:
                    item.append(Dc.subject(theme_name.strip()))
        for k in self.getLocalProperty('keywords', lang).split(','):
            item.append(Ut.keywords(k))
        item.extend(Ut.root(
            Ut.creator_mail(self.creator_email),
            Ut.contact_name(self.getLocalProperty('contact_person', lang)),
            Ut.contact_mail(self.getLocalProperty('contact_email', lang)),
            Ut.contact_phone(self.getLocalProperty('contact_phone', lang)),
            Ut.news_type(self.news_type),
            Ut.file_link(self.getLocalProperty('file_link', lang)),
            Ut.file_link_local(self.getLocalProperty('file_link_local', lang)),
            Ut.source_link(self.source_link),
            Ut.start_date(self.utShowFullDateTimeHTML(self.news_date)),
            Ut.save_date(self.utShowFullDateTimeHTML(self.bobobase_modification_time()))
        ))
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    #zmi actions
    def manage_FTPget(self):
        """ Return body for ftp """
        return self.description

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG

        self.copy_naaya_properties_from(self.version)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)

        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = semnews_item()
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject(): #Check if user can edit the content
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            self = self.version
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
        old_news_date = self.news_date
        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            if REQUEST is None:
                raise ValueError(form_errors.popitem()[1]) # pick a random error
            else:
                import transaction; transaction.abort() # because we already called _crete_NyZzz_object
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

        new_news_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('news_date', None))
        moved = False
        #If month or year changed then move the item to other folder
        if ((new_news_date.month(), new_news_date.year()) !=
            (old_news_date.month(), old_news_date.year())):
            self.news_date = new_news_date
            month_folder = create_month_folder(self.aq_parent.aq_parent.aq_parent, self.contributor, schema_raw_data)
            cut_data = self.aq_parent.manage_cutObjects([self.id, ])
            month_folder.manage_pasteObjects(cut_data)
            moved = True

        if 'file' in schema_raw_data: # Upload file
            self.handleUpload(schema_raw_data['file'])

        if schema_raw_data.get('discussion', None):
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1
        if moved:
            month_folder.recatalogNyObject(month_folder._getOb(self.getId()))
        else:
            self.recatalogNyObject(self)
        # Create log
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)

        zope.event.notify(NyContentObjectEditEvent(self, contributor))

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            if moved: #Redirect to moved location
                url = month_folder._getOb(self.id).absolute_url()
            else:
                url = self.absolute_url()
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (url, _lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semnews_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semnews_index')

    security.declareProtected(view, 'picture_html')
    def picture_html(self, REQUEST=None, RESPONSE=None):
        """ """
        REQUEST.RESPONSE.setHeader('content-type', 'text/html')
        return '<img src="getBigPicture" border="0" alt="" />'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT}, 'semnews_edit')

    security.declarePublic('downloadfilename')
    def downloadfilename(self, version=False):
        """ """
        context = self
        if version and self.hasVersion():
            context = self.version
        attached_file = context.get_data(as_string=False)
        filename = getattr(attached_file, 'filename', [])
        if not filename:
            return self.title_or_id()
        return filename[-1]

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        version = REQUEST.get('version', False)
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.getSize())
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename(version=version))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        if version and self.hasVersion():
            return semnews_item.index_html(self.version, REQUEST, RESPONSE)
        return semnews_item.index_html(self, REQUEST, RESPONSE)

    security.declarePublic('getDownloadUrl')
    def getDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

    security.declarePublic('getEditDownloadUrl')
    def getEditDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download?version=1'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

    def handleUpload(self, file):
        """
        Upload a file from disk.
        """
        filename = getattr(file, 'filename', '')
        if not filename:
            return
        self.manage_delObjects(self.objectIds())
        file_id = cookId('', '', file)[0]   #cleanup id
        self.manage_addFile(id=file_id, file=file)

InitializeClass(NySemNews)

#Custom folder listing
NaayaPageTemplateFile('zpt/semnews_folder_index', globals(),'semnews_folder_index')

config.update({
    'constructors': (manage_addNySemNews_html, addNySemNews),
    'folder_constructors': [
            ('manage_addNySemNews_html', manage_addNySemNews_html),
            ('semnews_add_html', semnews_add_html),
            ('addNySemNews', addNySemNews),
            ('import_NySemNews', importNySemNews),
        ],
    'add_method': addNySemNews,
    'validation': issubclass(NySemNews, NyValidation),
    '_class': NySemNews,
})

def get_config():
    return config
