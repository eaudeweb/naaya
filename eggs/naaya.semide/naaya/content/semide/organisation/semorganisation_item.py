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
import zope.event

#Naaya
from naaya.content.base.constants import MUST_BE_NONEMPTY, MUST_BE_POSITIV_INT, MUST_BE_DATETIME
from Products.NaayaBase.constants import (PERMISSION_EDIT_OBJECTS, EXCEPTION_NOTAUTHORIZED,
EXCEPTION_NOTAUTHORIZED_MSG, EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG,
EXCEPTION_STARTEDVERSION_MSG, MESSAGE_SAVEDCHANGES)

from Products.NaayaCore.managers.utils import make_id
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyValidation import NyValidation

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core import submitter

#module constants
METATYPE_OBJECT = 'Naaya Semide Organisation'
LABEL_OBJECT = 'Partner'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Organisation objects'
OBJECT_FORMS = ['semorganisation_add', 'semorganisation_edit']
OBJECT_CONSTRUCTORS = ['manage_addNySemOrganisation_html', 'semorganisation_add_html', 'addNySemOrganisation', 'importNySemOrganisation']
OBJECT_ADD_FORM = 'semorganisation_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide Organisation type.'
PREFIX_OBJECT = 'org'
PROPERTIES_OBJECT = {
    'id':                  (0, '', ''),
    'title':               (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':         (0, '', ''),
    'coverage':            (0, '', ''),
    'keywords':            (0, '', ''),
    'sortorder':           (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':         (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':          (0, '', ''),
    'org_type':            (0, '', ''),
    'address':             (0, '', ''),
    'org_url':             (0, '', ''),
    'org_coord':           (0, '', ''),
    'contact_title':       (0, '', ''),
    'contact_firstname':   (0, '', ''),
    'contact_lastname':    (0, '', ''),
    'contact_position':    (0, '', ''),
    'contact_email':       (0, '', ''),
    'contact_phone':       (0, '', ''),
    'contact_fax':         (0, '', ''),
    'lang':                (0, '', '')
}

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'org_coord':            dict(sortorder=100, widget_type="Checkbox", label="Project coordinator"),
    'org_type':             dict(sortorder=110, widget_type="Select", label="Organism type", list_id="organism_types"),
    'address':              dict(sortorder=120, widget_type="String", label="Address"),
    'org_url':              dict(sortorder=130, widget_type="String", label="Web site (URL)", default="http://"),
    'contact_title':        dict(sortorder=140, widget_type="String", label="Contact title", localized=True),
    'contact_firstname':    dict(sortorder=150, widget_type="String", label="Contact firstname", localized=True),
    'contact_lastname':     dict(sortorder=160, widget_type="String", label="Contact lastname", localized=True),
    'contact_position':     dict(sortorder=170, widget_type="String", label="Contact position", localized=True),
    'contact_email':        dict(sortorder=180, widget_type="String", label="Contant e-mail"),
    'contact_phone':        dict(sortorder=190, widget_type="String", label="Contact phone"),
    'contact_fax':          dict(sortorder=200, widget_type="String", label="Contact fax")
})
DEFAULT_SCHEMA['sortorder'].update(visible=False)

config = {
    'product': 'NaayaContent',
    'module': 'NySemOrganisation',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_OBJECT,
    'label': LABEL_OBJECT,
    'permission': PERMISSION_ADD_OBJECT,
    'forms': OBJECT_FORMS,
    'add_form': OBJECT_ADD_FORM,
    'description': DESCRIPTION_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'properties': PROPERTIES_OBJECT,
    'schema_name': 'NySemOrganisation',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySemOrganisation.gif'),
    '_misc': {
            'NySemOrganisation.gif': ImageFile('www/NySemOrganisation.gif', globals()),
            'NySemOrganisation_marked.gif': ImageFile('www/NySemOrganisation_marked.gif', globals()),
        },
}

manage_addNySemOrganisation_html = PageTemplateFile('zpt/semorganisation_manage_add', globals())
manage_addNySemOrganisation_html.kind = METATYPE_OBJECT
manage_addNySemOrganisation_html.action = 'addNySemOrganisation'

def semorganisation_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemOrganisation', 'form_helper': form_helper}, 'semorganisation_add')

def _create_NySemOrganisation_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NySemOrganisation(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNySemOrganisation(self, id='', contributor=None, REQUEST=None, **kwargs):
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

    ob = _create_NySemOrganisation_object(self, id, contributor)
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
            return REQUEST.RESPONSE.redirect('%s/semorganisation_add_html' % self.absolute_url())

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
        if l_referer == 'semorganisation_manage_add' or l_referer.find('semorganisation_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'semorganisation_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/semorganisation_add_html' % self.absolute_url())
    return ob.getId()

def importNySemOrganisation(self, param, id, attrs, content, properties, discussion, objects):
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
            ob = _create_NySemOrganisation_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            for prop in ob._get_schema().listPropNames():
                setattr(ob, prop, '')
            for k, v  in attrs.items():
                setattr(ob, k, v.encode('utf-8'))
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.submitThis()
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class semorganisation_item(Implicit, NyContentData):
    """ """
    meta_type = METATYPE_OBJECT

class NySemOrganisation(semorganisation_item, NyAttributes, NyItem, NyCheckControl, NyContentType, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemOrganisation.py'
    icon_marked = 'misc_/NaayaContent/NySemOrganisation_marked.gif'

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
        semorganisation_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('address', lang),
            self.getLocalProperty('contact_title', lang), self.getLocalProperty('contact_firstname', lang),
            self.getLocalProperty('contact_lastname', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'org_type="%s" org_url="%s" contact_email="%s" contact_phone="%s" contact_fax="%s" org_coord="%s"' % \
            (self.utXmlEncode(self.org_type),
                self.utXmlEncode(self.org_url),
                self.utXmlEncode(self.contact_email),
                self.utXmlEncode(self.contact_phone),
                self.utXmlEncode(self.contact_fax),
                self.utXmlEncode(self.org_coord))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<address lang="%s"><![CDATA[%s]]></address>' % (l, self.utToUtf8(self.getLocalProperty('address', l))))
            ra('<contact_title lang="%s"><![CDATA[%s]]></contact_title>' % (l, self.utToUtf8(self.getLocalProperty('contact_title', l))))
            ra('<contact_firstname lang="%s"><![CDATA[%s]]></contact_firstname>' % (l, self.utToUtf8(self.getLocalProperty('contact_firstname', l))))
            ra('<contact_lastname lang="%s"><![CDATA[%s]]></contact_lastname>' % (l, self.utToUtf8(self.getLocalProperty('contact_lastname', l))))
            ra('<contact_position lang="%s"><![CDATA[%s]]></contact_position>' % (l, self.utToUtf8(self.getLocalProperty('contact_position', l))))
        return ''.join(r)

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

        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = semorganisation_item()
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

        if form_errors:
            if REQUEST is None:
                raise ValueError(form_errors.popitem()[1]) # pick a random error
            else:
                import transaction; transaction.abort() # because we already called _crete_NyZzz_object
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

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
    manage_edit_html = PageTemplateFile('zpt/semorganisation_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semorganisation_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        REQUEST.RESPONSE.redirect('%s/index_html#%s' % (self.getParentNode().absolute_url(), self.id))

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semorganisation_edit')

InitializeClass(NySemOrganisation)

config.update({
   'constructors': (manage_addNySemOrganisation_html, addNySemOrganisation),
   'folder_constructors': [
           ('manage_addNySemOrganisation_html', manage_addNySemOrganisation_html),
           ('semorganisation_add_html', semorganisation_add_html),
           ('addNySemOrganisation', addNySemOrganisation),
           ('import_NySemOrganisation', importNySemOrganisation),
       ],
   'add_method': addNySemOrganisation,
   'validation': issubclass(NySemOrganisation, NyValidation),
   '_class': NySemOrganisation,
})

def get_config():
   return config
