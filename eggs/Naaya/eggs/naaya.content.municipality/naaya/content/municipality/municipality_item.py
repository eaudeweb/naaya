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
# Valentin Dumitru, Eau de Web

#Python imports
from copy import deepcopy
import os
import sys
from decimal import Decimal
from datetime import datetime

#Zope imports
from Persistence import Persistent
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from OFS.SimpleItem import Item
from zope.interface import implements
from zope.component import adapts
from zope.event import notify 
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyNonCheckControl import NyNonCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.content.bfile.NyBlobFile import make_blobfile
from Products.NaayaCore.managers.utils import utils, make_id

from interfaces import INyMunicipality

#module constants
METATYPE_OBJECT = 'Naaya Municipality'
LABEL_OBJECT = 'Municipality'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Municipality objects'
PERMISSION_EDIT_OBJECTS = 'Naaya - Edit Naaya Municipality objects'
OBJECT_FORMS = ['municipality_add', 'municipality_edit', 'municipality_index']
OBJECT_CONSTRUCTORS = ['municipality_add_html', 'addNyMunicipality']
OBJECT_ADD_FORM = 'municipality_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Municipality type.'
PREFIX_OBJECT = 'municipality'
ADDITIONAL_STYLE = open(ImageFile('www/municipality.css', globals()).path).read()

DEFAULT_SCHEMA = {
    'province': dict(sortorder=100, widget_type='Select', label='Province', required=True, list_id='provinces'),
    'municipality': dict(sortorder=110, widget_type='String', label='Municipality', required=True, localized=True),
    'contact_person': dict(sortorder=120, widget_type='String', label='Contact person', required=True),
    'email':    dict(sortorder=130, widget_type='String', label='Email address', required=True),
    'phone':    dict(sortorder=140, widget_type='String', label='Telephone number'),
    'choice':   dict(sortorder=150, widget_type='Select', label='Our municipality:', required=True, list_id='ambassador_choices'),
    'explain_why': dict(sortorder=200, widget_type='TextArea', label='Please explain why you chose this / these species:', localized=True, tinymce=True),
    'explain_how': dict(sortorder=210, widget_type='TextArea', label='Please explain how you chose this / these species:', localized=True, tinymce=True),
    'importance1': dict(sortorder=220, widget_type='TextArea', label='The selected ambassador species is / are important to our municipality because:', localized=True, tinymce=True),
    'importance2': dict(sortorder=230, widget_type='TextArea', label='Our municipality is important for the ambassador species because:', localized=True, tinymce=True),
    'usage': dict(sortorder=240, widget_type='TextArea', label='Please explain how you use the ambassador species in your municipality:', localized=True, tinymce=True),
    'link1': dict(sortorder=250, widget_type='String', label='Interesting links:'),
    'link2': dict(sortorder=260, widget_type='String', label='Interesting links:'),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['title'].update(visible=False, required=False)
DEFAULT_SCHEMA['description'].update(visible=False)
DEFAULT_SCHEMA['geo_location'].update(visible=False)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

def setupContentType(site):
    from skel import PROVINCES, AMBASSADOR_CHOICES
    ptool = site.getPortletsTool()
    iprovinces = getattr(ptool, 'provinces', None)
    if not iprovinces:
        ptool.manage_addRefTree('provinces')
        for k, v in PROVINCES.items():
            ptool.provinces.manage_addRefTreeNode(k, v)
    ichoices = getattr(ptool, 'ambassador_choices', None)
    if not ichoices:
        ptool.manage_addRefTree('ambassador_choices')
        for k, v in AMBASSADOR_CHOICES.items():
            ptool.ambassador_choices.manage_addRefTreeNode(k, v)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'municipality_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyMunicipality',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyMunicipality.gif'),
        'on_install' : setupContentType,
        'additional_style': ADDITIONAL_STYLE,
        '_misc': {
                'NyMunicipality.gif': ImageFile('www/NyMunicipality.gif', globals()),
                'NyMunicipality_marked.gif': ImageFile('www/NyMunicipality_marked.gif', globals()),
            },
    }

def municipality_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyMunicipality', 'form_helper': form_helper}, 'municipality_add')

def _create_NyMunicipality_object(parent, id, title, contributor):
    id = make_id(parent, id=id, title=title, prefix='municipality')
    ob = NyMunicipality(id, title, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.species = []
    ob.after_setObject()
    return ob

def addNyMunicipality(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Municipality type of object.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    _title = '%s, %s' % (schema_raw_data.get('municipality',''),
                        self.get_node_title('provinces', schema_raw_data.get('province','')))
    schema_raw_data['title'] = _title
    _contact_word = schema_raw_data.get('contact_word', '')

    #process parameters
    id = make_id(self, id=id, title=_title, prefix='municipality')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyMunicipality_object(self, id, _title, contributor)

    ambassador_species = schema_raw_data.pop('ambassador_species', '')
    ambassador_species_description = schema_raw_data.pop('ambassador_species_description', '')
    ambassador_species_picture = schema_raw_data.pop('ambassador_species_picture', None)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    ob.process_species(ambassador_species, ambassador_species_description, ambassador_species_picture, form_errors)

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
            ob.setSession('ambassador_species', ambassador_species)
            ob.setSession('ambassador_species_description', ambassador_species_description)
            REQUEST.RESPONSE.redirect('%s/municipality_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'municipality_manage_add' or l_referer.find('municipality_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'municipality_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)

    return ob.getId()

class AmbassadorSpecies(Persistent):
    def __init__(self, title, description='', picture=None):
        self.title = title
        self.description = description
        picture_test = picture is not None and picture.filename
        if picture_test:
            self.picture = make_blobfile(picture, removed=False, timestamp=datetime.utcnow())
        else:
            self.picture = None

class NyMunicipality(NyContentData, NyAttributes, NyItem, NyNonCheckControl, NyValidation, NyContentType, utils):
    """ """
    implements(INyMunicipality)
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyMunicipality.gif'
    icon_marked = 'misc_/NaayaContent/NyMunicipality_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, contributor):
        """ """
        self.id = id
        NyContentData.__dict__['__init__'](self)
        NyValidation.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'obfuscated_email')
    def obfuscated_email(self):
        ret = self.email
        if self.email:
            if isinstance(self.email, unicode):
                self.email = self.email.encode('UTF-8')
            ret = self.email.replace('@', ' at ')
        return ret

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            obj = self.version
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        else:
            obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)

        schema_raw_data['title'] = obj.title

        delete_species = sorted(list(schema_raw_data.pop('delete_species', '')), reverse=True)
        for list_index in delete_species:
            self.species.pop(int(list_index))

        ambassador_species = schema_raw_data.pop('ambassador_species', '')
        ambassador_species_description = schema_raw_data.pop('ambassador_species_description', '')
        ambassador_species_picture = schema_raw_data.pop('ambassador_species_picture', None)

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        self.process_species(ambassador_species, ambassador_species_description,\
                        ambassador_species_picture, form_errors)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                self.setSession('ambassador_species', ambassador_species)
                self.setSession('ambassador_species_description', ambassador_species_description)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

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
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'municipality_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'municipality_edit')

    security.declareProtected(PERMISSION_ADD_OBJECT, 'process_species')
    def process_species(self, ambassador_species, ambassador_species_description,
                        ambassador_species_picture, form_errors):
        picture_test = ambassador_species_picture is not None and ambassador_species_picture.filename
        if (ambassador_species_description or picture_test) and not ambassador_species:
            form_errors['ambassador_species'] = ['The species name is mandatory!']
        elif ambassador_species:
            new_species = AmbassadorSpecies(ambassador_species,
                                            ambassador_species_description,
                                            ambassador_species_picture)
            self.species.append(new_species)

    security.declareProtected(view, 'render_picture')
    def render_picture(self, RESPONSE, list_index=0):
        """ Render municipality picture """
        list_index = int(list_index)
        if len(self.species) > list_index and self.species[list_index].picture is not None:
            return self.species[list_index].picture.send_data(RESPONSE, as_attachment=False)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang),
            self.municipality,
            self.specieskeywords(),
            self.html2text(self.getLocalProperty('explain_why', lang)),
            self.html2text(self.getLocalProperty('explain_how', lang)),
            self.html2text(self.getLocalProperty('importance1', lang)),
            self.html2text(self.getLocalProperty('importance2', lang)),
            self.html2text(self.getLocalProperty('usage', lang))]
            )

    security.declarePrivate('specieskeywords')
    def specieskeywords(self):
        if len(self.species) > 0:
            species = ['%s %s' % (ob.title, self.html2text(ob.description)) for ob in self.species]
            return u' '.join(species)
        return ''

InitializeClass(NyMunicipality)

config.update({
    'constructors': (municipality_add_html, addNyMunicipality),
    'folder_constructors': [
            ('municipality_add_html', municipality_add_html),
            ('addNyMunicipality', addNyMunicipality),
        ],
    'add_method': addNyMunicipality,
    'validation': issubclass(NyMunicipality, NyValidation),
    '_class': NyMunicipality,
})

def get_config():
    return config
