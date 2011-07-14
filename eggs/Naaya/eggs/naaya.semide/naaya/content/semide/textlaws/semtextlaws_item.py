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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
# Alexandru Plugaru, Eau de Web

#Python
import os
import sys
from copy import deepcopy

#Zope
from Acquisition import Implicit
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile
from OFS.Image import cookId
import zope.event

#Naaya
from naaya.content.base.constants import MUST_BE_NONEMPTY, MUST_BE_POSITIV_INT, MUST_BE_DATETIME
from Products.NaayaBase.constants import (PERMISSION_EDIT_OBJECTS, EXCEPTION_NOTAUTHORIZED,
EXCEPTION_NOTAUTHORIZED_MSG, EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG,
EXCEPTION_STARTEDVERSION_MSG, MESSAGE_SAVEDCHANGES)

from Products.NaayaCore.managers.utils import utils, make_id, get_nsmap
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyBase import rss_item_for_object

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core import submitter

from lxml import etree
from lxml.builder import ElementMaker

#module constants
METATYPE_OBJECT = 'Naaya Semide Text of Laws'
LABEL_OBJECT = 'Text of laws'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Text of Laws objects'
OBJECT_FORMS = ['semtextlaws_add', 'semtextlaws_edit', 'semtextlaws_index']
OBJECT_CONSTRUCTORS = ['manage_addNySemTextLaws_html', 'semtextlaws_add_html', 'addNySemTextLaws', 'importNySemTextLaws']
OBJECT_ADD_FORM = 'semtextlaws_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide Text of Laws type.'
PREFIX_OBJECT = 'stl'
PROPERTIES_OBJECT = {
    'id':                   (0, '', ''),
    'title':                (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':          (0, '', ''),
    'coverage':             (0, '', ''),
    'keywords':             (0, '', ''),
    'sortorder':            (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':          (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':           (0, '', ''),
    'source':               (0, '', ''),
    'source_link':          (0, '', ''),
    'subject':              (0, '', ''),
    'relation':             (0, '', ''),
    'geozone':              (0, '', ''),
    'file_link':            (0, '', ''),
    'file_link_local':      (0, '', ''),
    'official_journal_ref': (0, '', ''),
    'type_law':             (0, '', ''),
    'original_language':    (0, '', ''),
    'statute':              (0, '', ''),
    'lang':                 (0, '', ''),
    'file':                 (0, '', ''),
}
DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'type_law':             dict(sortorder=110, widget_type="Select", label="Type", list_id='text_laws'),
    'official_journal_ref': dict(sortorder=120, widget_type="String", label="Official journal reference", localized=True),
    'source':               dict(sortorder=130, widget_type="String", label="Source", localized=True),
    'source_link':          dict(sortorder=140, widget_type="String", label="Source link", default="http://"),
    'geozone':              dict(sortorder=150, widget_type="Select", label="Geozone", list_id='event_geozone'),
    'statute':              dict(sortorder=160, widget_type="Select", label="Status", list_id='status_types'),
    'original_language':    dict(sortorder=170, widget_type="Select", label="Original language", glossary_id='glossary_languages'),
    'relation':             dict(sortorder=180, widget_type="String", label="Relation"),
    'subject':              dict(sortorder=190, widget_type="SelectMultiple", label="Subject"),
    'file_link':            dict(sortorder=200, widget_type="String", label="File link", default='http://'),
})
DEFAULT_SCHEMA['sortorder'].update(visible=False)

config = {
    'product': 'NaayaContent',
    'module': 'NySemTextLaws',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_OBJECT,
    'label': LABEL_OBJECT,
    'permission': PERMISSION_ADD_OBJECT,
    'forms': OBJECT_FORMS,
    'add_form': OBJECT_ADD_FORM,
    'description': DESCRIPTION_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'properties': PROPERTIES_OBJECT,
    'schema_name': 'NySemTextLaws',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySemTextLaws.gif'),
    '_misc': {
            'NySemTextLaws.gif': ImageFile('www/NySemTextLaws.gif', globals()),
            'NySemTextLaws_marked.gif': ImageFile('www/NySemTextLaws_marked.gif', globals()),
        },
}

manage_addNySemTextLaws_html = PageTemplateFile('zpt/semtextlaws_manage_add', globals())
manage_addNySemTextLaws_html.kind = METATYPE_OBJECT
manage_addNySemTextLaws_html.action = 'addNySemTextLaws'

def semtextlaws_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemTextLaws', 'form_helper': form_helper}, 'semtextlaws_add')

def _create_NySemTextLaws_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NySemTextLaws(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNySemTextLaws(self, id='', contributor=None, REQUEST=None, **kwargs):
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

    ob = _create_NySemTextLaws_object(self, id, contributor)
    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/semtextlaws_add_html' % self.absolute_url())

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
        if l_referer == 'semtextlaws_manage_add' or l_referer.find('semtextlaws_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'semtextlaws_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/semtextlaws_add_html' % self.absolute_url())
    return ob.getId()


def importNySemTextLaws(self, param, id, attrs, content, properties, discussion, objects):
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
            ob = _create_NySemTextLaws_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
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
                except TypeError, ValueError:
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


class semtextlaws_item(Implicit, NyContentData, NyFSContainer):
    """ """
    meta_type = METATYPE_OBJECT

class NySemTextLaws(semtextlaws_item, NyAttributes, NyItem, NyCheckControl, NyContentType, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemTextLaws.gif'
    icon_marked = 'misc_/NaayaContent/NySemTextLaws_marked.gif'

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
        semtextlaws_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'resource_type')
    def resource_type(self):
        return self.type_law

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(self.subject)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'type_law="%s" file_link="%s" file_link_local="%s" official_journal_ref="%s" source_link="%s" subject="%s" relation="%s" geozone="%s" original_language="%s" statute="%s"' % \
               (self.utXmlEncode(self.type_law),
                self.utXmlEncode(self.file_link),
                self.utXmlEncode(self.file_link_local),
                self.utXmlEncode(self.official_journal_ref),
                self.utXmlEncode(self.source_link),
                self.utXmlEncode(self.subject),
                self.utXmlEncode(self.relation),
                self.utXmlEncode(self.geozone),
                self.utXmlEncode(self.utNoneToEmpty(self.original_language)),
                self.utXmlEncode(self.statute))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
        if self.getSize():
            ra('<item file="%s" content_type="%s" size="%s" name="%s"/>' % (
                self.utBase64Encode(str(self.utNoneToEmpty(self.get_data()))),
                self.utXmlEncode(self.getContentType()),
                self.getSize(),
                self.downloadfilename())
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
            Dc.type(self.type_law),
            Dc.format(self.format()),
            Dc.source(self.getLocalProperty('source', lang)),
            Dc.creator(l_site.getLocalProperty('creator', lang)),
            Dc.publisher(l_site.getLocalProperty('publisher', lang)),
            Dc.relation(self.relation)
            ))
        for k in self.subject:
            if k:
                theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
                theme_name = theme_ob.theme_name
                if theme_name:
                    item.append(Dc.subject(theme_name.strip()))
        item.extend(Dc.root(
            Ut.type_law(self.type_law),
            Ut.file_link(self.file_link),
            #Ut.file_link_local(self.file_link_local),
            Ut.official_journal_ref(self.getLocalProperty('official_journal_ref', lang)),
            Ut.source_link(self.source_link),
            Ut.geozone(self.geozone),
            Ut.original_language(self.original_language),
            Ut.statute(self.statute)
        ))
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = self.gl_get_selected_language()
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        self.updatePropertiesFromGlossary(_lang)

        approved = schema_raw_data.get('approved', None)
        if  approved != self.approved:
            if approved == 0:
                approved_by = None
            else:
                approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)

        self._p_changed = 1

        if 'file' in schema_raw_data: # Upload file
            self.handleUpload(schema_raw_data['file'])

        if schema_raw_data.get('discussion', None):
            self.open_for_comments()
        else:
            self.close_for_comments()

        self.recatalogNyObject(self)

        if REQUEST: return REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

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
        self.version = semtextlaws_item()
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

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        self.start_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('start_date', None))
        self.end_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('end_date', None))

        if form_errors:
            if REQUEST is None:
                raise ValueError(form_errors.popitem()[1]) # pick a random error
            else:
                import transaction; transaction.abort() # because we already called _crete_NyZzz_object
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

        if 'file' in schema_raw_data: # Upload file
            self.handleUpload(schema_raw_data['file'])

        if schema_raw_data.get('discussion', None):
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)

        # Create log
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)

        zope.event.notify(NyContentObjectEditEvent(self, contributor))

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semtextlaws_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semtextlaws_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semtextlaws_edit')

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
            return semtextlaws_item.index_html(self.version, REQUEST, RESPONSE)
        return semtextlaws_item.index_html(self, REQUEST, RESPONSE)

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

InitializeClass(NySemTextLaws)

config.update({
    'constructors': (manage_addNySemTextLaws_html, semtextlaws_add_html, addNySemTextLaws),
    'folder_constructors': [
            ('manage_addNySemTextLaws_html', manage_addNySemTextLaws_html),
            ('semtextlaws_add_html', semtextlaws_add_html),
            ('addNySemTextLaws', addNySemTextLaws),
            ('import_NySemTextLaws', importNySemTextLaws),
        ],
    'add_method': addNySemTextLaws,
    'validation': issubclass(NySemTextLaws, NyValidation),
    '_class': NySemTextLaws,
})

def get_config():
    return config
