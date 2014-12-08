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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

#Python imports
from copy import deepcopy
import os
import sys

#Zope imports
from Globals import InitializeClass
from zope import event as zope_event
from OFS.event import ObjectWillBeRemovedEvent
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from publication_item import publication_item
from permissions import PERMISSION_ADD_PUBLICATION
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent

#module constants
METATYPE_OBJECT = 'Naaya Publication'
LABEL_OBJECT = 'Publication'
OBJECT_FORMS = ['publication_add', 'publication_edit', 'publication_index']
OBJECT_CONSTRUCTORS = ['manage_addNyPublication_html', 'publication_add_html', 'addNyPublication', 'importNyPublication']
OBJECT_ADD_FORM = 'publication_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Publication type. It can be used for published articles or books.'
PREFIX_OBJECT = 'pub'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'locator':      (1, MUST_BE_NONEMPTY, 'The Publication field must have a value.'),
    'lang':         (0, '', '')
}
DEFAULT_SCHEMA = {
    'original_title':   dict(sortorder=11, widget_type='String', label='Original title'),
    'author':           dict(sortorder=12, widget_type='String', label='Author'),
    'publisher':        dict(sortorder=13, widget_type='String', label='Publisher'),
    'editor':           dict(sortorder=14, widget_type='String', label='Editor'),
    'publication_year': dict(sortorder=15, widget_type='String', data_type='int', label='Publication year'),
    'volume':           dict(sortorder=16, widget_type='String', label='Volume'),
    'issue_no':         dict(sortorder=17, widget_type='String', label='Issue No.'),
    'issue_date':       dict(sortorder=18, widget_type='Date', data_type='date', label='Issue date'),
    'description':      dict(sortorder=20, widget_type='TextArea', label='Short description of content', localized=True, tinymce=True),
    'pages':            dict(sortorder=80, widget_type='String', data_type='int', label='Page(s)'),
    'document_type':    dict(sortorder=90, widget_type='String', label='Document type'),
    'isbn':             dict(sortorder=100, widget_type='String', label='ISBN'),
    'languages':        dict(sortorder=110, widget_type='String', label='Language(s)'),
    'locator':          dict(sortorder=120, widget_type='String', label='Internet access (URL)', localized=True),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
# make sure the label is the one we wanted
DEFAULT_SCHEMA['description'].update({'label': 'Short description of content'})

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'NyPublication',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Publication',
        'label': 'Publication',
        'permission': PERMISSION_ADD_PUBLICATION,
        'forms': ['publication_add', 'publication_edit', 'publication_index'],
        'add_form': 'publication_add_html',
        'description': 'This is Naaya Publication type. It can be used for published articles or books.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyPublication',
        'import_string': 'importNyPublication',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyPublication.gif'),
        '_misc': {
                'NyPublication.gif': ImageFile('www/NyPublication.gif', globals()),
                'NyPublication_marked.gif': ImageFile('www/NyPublication_marked.gif', globals()),
            },
    }

def publication_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyPublication', 'form_helper': form_helper}, 'publication_add')

def _create_NyPublication_object(parent, id, title, file, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyPublication(id, title, file, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyPublication(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Publication type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('locator', '')
    _source = schema_raw_data.pop('source', 'file')
    _file = schema_raw_data.pop('file', '')
    _url = schema_raw_data.pop('url', '')
    _contact_word = schema_raw_data.get('contact_word', '')

    title = schema_raw_data.get('title', '')
    id = self.utSlugify(id or schema_raw_data.get('title', '') or PREFIX_OBJECT)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyPublication_object(self, id, title, '', contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/publication_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()
    ob.handleUpload(_source, _file, _url)

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'publication_manage_add' or l_referer.find('publication_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'publication_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

    return ob.getId()

def importNyPublication(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyPublication_object(self, id, id, '', self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.checkThis(attrs['validation_status'].encode('utf-8'),
                attrs['validation_comment'].encode('utf-8'),
                attrs['validation_by'].encode('utf-8'),
                attrs['validation_date'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NyPublication(publication_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    icon = 'misc_/NaayaContent/NyPublication.gif'
    icon_marked = 'misc_/NaayaContent/NyPublication_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, file, contributor):
        """ """
        self.id = id
        publication_item.__init__(self, id, title, file)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
                (self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<locator lang="%s"><![CDATA[%s]]></locator>' % (l, self.utToUtf8(self.getLocalProperty('locator', l))))
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        raise EXCEPTION_NOTIMPLEMENTED('commitVersion')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        raise EXCEPTION_NOTIMPLEMENTED('startVersion')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)

        _source = schema_raw_data.pop('source', 'file')
        _file = schema_raw_data.pop('file', '')
        _url = schema_raw_data.pop('url', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            # Upload file
            if _source:
                self.saveUpload(source=_source, file=_file, url=_url, lang=_lang)

            if self.discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, source='file', file='', url='', lang=None, REQUEST=None):
        """ """
        if REQUEST:
            username = REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            username = self.REQUEST.AUTHENTICATED_USER.getUserName()

        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        if lang is None:
            lang = self.gl_get_selected_language()

        context = self

        ext_file = self.get_data(as_string=False)
        zope_event.notify(ObjectWillBeRemovedEvent(
            ext_file, self, ext_file.getId()))

        context.handleUpload(source, file, url)
        self.recatalogNyObject(self)

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/publication_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'publication_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'publication_edit')


    def downloadfilename(self):
        """ Return download file name
        """
        context = self
        filename = context._get_data_name()
        return filename or context.title_or_id()

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.size)
        filename = self.utToUtf8(self.downloadfilename())
        filename = self.utCleanupId(filename)
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + filename)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return publication_item.index_html(self, REQUEST, RESPONSE)

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return publication_item.index_html(self, REQUEST, RESPONSE)

    security.declarePublic('getDownloadUrl')
    def getDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        return self.absolute_url() + '/download'

    security.declarePublic('getEditDownloadUrl')
    def getEditDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        return self.absolute_url() + '/download?version=1'

InitializeClass(NyPublication)

manage_addNyPublication_html = PageTemplateFile('zpt/publication_manage_add', globals())
manage_addNyPublication_html.kind = METATYPE_OBJECT
manage_addNyPublication_html.action = 'addNyPublication'
config.update({
    'constructors': (manage_addNyPublication_html, addNyPublication),
    'folder_constructors': [
            # NyFolder.manage_addNyPublication_html = manage_addNyPublication_html
            ('manage_addNyPublication_html', manage_addNyPublication_html),
            ('publication_add_html', publication_add_html),
            ('addNyPublication', addNyPublication),
            (config['import_string'], importNyPublication),
        ],
    'add_method': addNyPublication,
    'validation': issubclass(NyPublication, NyValidation),
    '_class': NyPublication,
})

def get_config():
    return config
