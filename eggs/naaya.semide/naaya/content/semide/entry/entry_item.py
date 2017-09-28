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
# Alexandru Plugaru, Eau de Web










#DEPRECATED
#DEPRECATED
#DEPRECATED











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
import zope.event

#Naaya
import naaya.content.base.constants
import Products.NaayaBase.constants

from Products.NaayaCore.managers.utils import make_id
from Products.NaayaCore.managers.utils import utils

from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent

#module constants
METATYPE_OBJECT = 'Naaya Entry'
LABEL_OBJECT = 'Entry'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Entry objects'
OBJECT_FORMS = ['entry_add', 'entry_edit', 'entry_index']
OBJECT_CONSTRUCTORS = ['manage_addNyEntry_html', 'entry_add_html', 'addNyEntry', 'importNyEntry']
OBJECT_ADD_FORM = 'entry_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Entry type.'
PREFIX_OBJECT = 'pnt'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, naaya.content.base.constants.MUST_BE_NONEMPTY, 'The surname field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, naaya.content.base.constants.MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, naaya.content.base.constants.MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'creator':      (0, '', ''),
    'creator_email':(0, '', ''),
    'rights':       (0, '', ''),
    'document_type':(0, '', ''),
    'entry':        (0, '', ''),
    'lang':         (0, '', '')
}

DEFAULT_SCHEMA = NY_CONTENT_BASE_SCHEMA
DEFAULT_SCHEMA['sortorder'].update(visible=False)

config = {
    'product': 'NaayaContent', 
    'module': 'NyEntry',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_OBJECT,
    'label': LABEL_OBJECT,
    'permission': PERMISSION_ADD_OBJECT,
    'forms': OBJECT_FORMS,
    'add_form': OBJECT_ADD_FORM,
    'description': DESCRIPTION_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'properties': PROPERTIES_OBJECT,
    'schema_name': 'NyEntry',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyEntry.gif'),
    '_misc': {
            'NyEntry.gif': ImageFile('www/NyEntry.gif', globals()),
            'NyEntry_marked.gif': ImageFile('www/NyEntry_marked.gif', globals()),
        },
}

manage_addNyEntry_html = PageTemplateFile('zpt/entry_manage_add', globals())
manage_addNyEntry_html.kind = METATYPE_OBJECT
manage_addNyEntry_html.action = 'addNyEntry'

def entry_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyEntry'}, 'entry_add')

def _create_NyEntry_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NyEntry(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyEntry(self, id='', REQUEST=None, contributor=None, **kwargs):
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
    
    ob = _create_NyEntry_object(self, id, contributor)
        
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
            return REQUEST.RESPONSE.redirect('%s/entry_add_html' % self.absolute_url())
    
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
        if l_referer == 'entry_manage_add' or l_referer.find('entry_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'entry_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/entry_add_html' % self.absolute_url())
    return ob.getId()
    
def importNyEntry(self, param, id, attrs, content, properties, discussion, objects):
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
            addNyEntry(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                entry=attrs['entry'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            for property, langs in properties.items():
                for lang in langs:
                    ob._setLocalPropValue(property, lang, langs[lang])
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

class entry_item(Implicit, NyContentData):
    """ """
    
class NyEntry(entry_item, NyAttributes, NyItem, NyCheckControl, NyContentType, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyEntry.gif'
    icon_marked = 'misc_/NaayaContent/NyEntry_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += entry_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        entry_item.__init__(self)
        NyCheckControl.__init__(self)
        NyItem.__init__(self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'entry="%s" validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
            (self.utXmlEncode(self.entry),
                self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """

    #site actions
    security.declareProtected(Products.NaayaBase.constants.PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self._local_properties_metadata = deepcopy(self.version._local_properties_metadata)
        self._local_properties = deepcopy(self.version._local_properties)
        self.sortorder = self.version.sortorder
        self.entry = self.version.entry
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(Products.NaayaBase.constants.PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        #check permissions
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = entry_item(self.title, self.description, self.coverage, self.keywords, self.sortorder,
            self.entry, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(Products.NaayaBase.constants.PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        
    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/entry_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'entry_index')

    security.declareProtected(Products.NaayaBase.constants.PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'entry_edit')

InitializeClass(NyEntry)

config.update({
    'constructors': (manage_addNyEntry_html, addNyEntry),
    'folder_constructors': [
            ('manage_addNyEntry_html', manage_addNyEntry_html),
            ('entry_add_html', entry_add_html),
            ('addNyEntry', addNyEntry),
        ],
    'add_method': addNyEntry,
    'validation': issubclass(NyEntry, NyValidation),
    '_class': NyEntry,
})

def get_config():
    return config