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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
# Cristian Romanescu, Eau de Web
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED,\
    EXCEPTION_NOTAUTHORIZED_MSG, PERMISSION_EDIT_OBJECTS, MESSAGE_SAVEDCHANGES,\
    EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG, EXCEPTION_NOVERSION,\
    EXCEPTION_NOVERSION_MSG

#Python imports
from copy import deepcopy
from datetime import datetime
import os, sys
import simplejson as json
from decimal import Decimal

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Acquisition import Implicit
from OFS.SimpleItem import Item
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements
from zope.component import adapts
from zope.event import notify 
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent
from Products.NaayaCore.interfaces import ICSVImportExtraColumns

from interfaces import INyOrganisation

from naaya.content.bfile.NyBlobFile import make_blobfile
#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.managers.utils import make_id

from naaya.content.expnet_common.expnet_mixin import ExpnetMixin

from permissions import PERMISSION_ADD_ORGANISATION

METATYPE_OBJECT = 'Naaya Organisation'

DEFAULT_SCHEMA = {
    'webpage': dict(sortorder=120, widget_type='String', label='Webpage'),
    'phone':   dict(sortorder=140, widget_type='String', label='Phone'),
    'fax':     dict(sortorder=160, widget_type='String', label='Fax'),
    'email':   dict(sortorder=170, widget_type='String', label='Email address'),
    'contact_details': dict(sortorder=230, widget_type='TextArea',
                            label='Contact details'),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)
DEFAULT_SCHEMA['geo_location'].update(visible=True)

def setupContentType(site):
    from naaya.content.expnet_common.skel import setup_expnet_skel
    setup_expnet_skel(site)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'organisation_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': 'Organisation',
        'permission': PERMISSION_ADD_ORGANISATION,
        'forms': ['organisation_add', 'organisation_edit', 'organisation_index'],
        'add_form': 'organisation_add_html',
        'description': 'This is Naaya Organisation type.',
        'properties': {}, #TODO: REMOVE
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyOrganisation',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyOrganisation.gif'),
        'on_install' : setupContentType,
        '_misc': {
                'NyOrganisation.gif': ImageFile('www/NyOrganisation.gif', globals()),
                'NyOrganisation_marked.gif': ImageFile('www/NyOrganisation_marked.gif', globals()),
            },
    }

def organisation_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyOrganisation', 'form_helper': form_helper}, 'organisation_add')

def _create_NyOrganisation_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='organisation')
    ob = NyOrganisation(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyOrganisation(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Organisation type of object.
    """
    #process parameters
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('details', '')
    schema_raw_data.setdefault('resourceurl', '')
    schema_raw_data.setdefault('source', '')
    schema_raw_data.setdefault('topitem', '')
    _organisation_word = schema_raw_data.get('organisation_word', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix='organisation')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyOrganisation_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_organisation_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/organisation_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    #Process uploaded file
    ob.picture = None
    _uploaded_file = schema_raw_data.pop('organisation_picture', None)
    if _uploaded_file is not None and _uploaded_file.filename:
        ob.picture = make_blobfile(_uploaded_file,
                           removed=False,
                           timestamp=datetime.utcnow())

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'organisation_manage_add' or l_referer.find('organisation_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'organisation_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyOrganisation(self, param, id, attrs, content, properties, discussion, objects):
    """
    @todo: Not implemented 
    """
    raise NotImplementedError


class organisation_item(Implicit, NyContentData):
    """ """
    pass

class NyOrganisation(organisation_item, NyAttributes, NyItem, NyCheckControl, NyContentType, ExpnetMixin):
    """ """

    implements(INyOrganisation)
    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyOrganisation.gif'
    icon_marked = 'misc_/NaayaContent/NyOrganisation_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        #if not self.hasVersion():
        #    l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += organisation_item.manage_options(self)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        organisation_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'personaltitle="%s" firstname="%s" lastname="%s" department="%s" organisation="%s" postaladdress="%s" phone="%s" fax="%s" cellphone="%s" email="%s" webpage="%s"' % \
            (self.utXmlEncode(self.personaltitle), 
            self.utXmlEncode(self.firstname), 
            self.utXmlEncode(self.lastname), 
            self.utXmlEncode(self.department), 
            self.utXmlEncode(self.organisation), 
            self.utXmlEncode(self.postaladdress), 
            self.utXmlEncode(self.phone), 
            self.utXmlEncode(self.fax), 
            self.utXmlEncode(self.cellphone), 
            self.utXmlEncode(self.email), 
            self.utXmlEncode(self.webpage))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<personaltitle lang="%s"><![CDATA[%s]]></personaltitle>' % (l, self.utToUtf8(self.getLocalProperty('personaltitle', l))))
            ra('<jobtitle lang="%s"><![CDATA[%s]]></jobtitle>' % (l, self.utToUtf8(self.getLocalProperty('jobtitle', l))))
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
        user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if (not self.checkPermissionEditObject()) or (
            self.checkout_user != user):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.copy_naaya_properties_from(self.version)
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        notify(NyContentObjectEditEvent(self, user))
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
        self.version = organisation_item()
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

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

        #Process uploaded file
        _uploaded_file = schema_raw_data.pop('organisation_picture', None)
        if _uploaded_file is not None and _uploaded_file.filename:
            self.picture = make_blobfile(_uploaded_file,
                               removed=False,
                               timestamp=datetime.utcnow())


        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
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

    #zmi pages
    #security.declareProtected(view_management_screens, 'manage_edit_html')
    #manage_edit_html = PageTemplateFile('zpt/organisation_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'organisation_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'organisation_edit')
    
    def render_picture(self, RESPONSE):
        """ Render organisation picture """
        if hasattr(self, 'picture') and self.picture:
                return self.picture.send_data(RESPONSE, as_attachment=False)

    def delete_picture(self, REQUEST=None):
        """ Delete attached organisation picture """
        self.picture = None
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/edit_html' % (self.absolute_url()))

    _minimap_template = PageTemplateFile('zpt/minimap', globals())
    def minimap(self):
        if self.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.geo_location.lat, 'lon': self.geo_location.lon}]
        elif self.aq_parent.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.aq_parent.geo_location.lat, 'lon': self.aq_parent.geo_location.lon}]
        else:
            return ""
        json_simplepoints = json.dumps(simplepoints, default=json_encode)
        return self._minimap_template(points=json_simplepoints)

    def list_employees(self):
        ctool = self.getCatalogTool()
        contacts = ctool.search({'meta_type' : 'Naaya Expert'}) #@WARNING: Hard-coded meta_type
        ret_current = []
        ret_previous = []
        for brain in contacts:
            contact = brain.getObject()
            for record in contact.employment_history:
                if record.organisation == self.title:
                    if record.current:
                        ret_current.append(contact)
                    else:
                        ret_previous.append(contact)
        return (ret_current, ret_previous)

    def has_coordinates(self):
        """ check if the current object has map coordinates"""
        if self.geo_location:
            return self.geo_location.lat and self.geo_location.lon
        return False

    def obfuscated_email(self):
        ret = self.email
        if self.email:
            if isinstance(self.email, unicode):
                self.email = self.email.encode('UTF-8')
            ret = self.email.replace('@', ' at ')
        return ret

class OrganisationCSVImportAdapter(object):
    implements(ICSVImportExtraColumns)
    adapts(INyOrganisation)
    def __init__(self, ob):
        self.ob = ob
    def handle_columns(self, extra_properties):
        ob_owner = extra_properties.get('_object_owner')
        if ob_owner:
            try:
                acl_users = self.ob.getSite().getAuthenticationTool()
                user = acl_users.getUserById(ob_owner).__of__(acl_users)
            except:
                return "Requested owner %s is not in the portal users table" % str(ob_owner)
            self.ob.changeOwnership(user=user)

            #Send confirmation email to the owner
            email_body = 'The organisation %s was created within the biodiversity portal biodiversiteit.nl.\n\n You can view or edit details of this organisation by following this link:\n\n %s \n\n' % (self.ob.title, self.ob.absolute_url())
            email_to = user.email
            email_from = 'no-reply@biodiversiteit.nl'
            email_subject = '%s organisation was created' % self.ob.title
            self.ob.getEmailTool().sendEmail(email_body, email_to, email_from, email_subject)

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

InitializeClass(NyOrganisation)


#
class OrganisationLister(Implicit, Item):

    _index_template = NaayaPageTemplateFile('zpt/organisations_list', globals(), 'organisation')

    """
    Plug into the catalog to retrieve the list of organisations
    Render the list of organisations recorded for this site.
    """
    def __init__(self, id):
        self.id = id


    def index_html(self, REQUEST):
        """ Index page """
        return self._index_template(REQUEST)

    def items_in_topic(self, topic=None, filter_name=None, objects=False):
        filters = {'meta_type' : METATYPE_OBJECT, 'approved': True}
        if topic is not None:
            default_lang = self.gl_get_default_language()
            default_lang_name = self.gl_get_language_name(default_lang)
            glossary = self.getSite().chm_terms
            try:
                item_brains = glossary.getObjectByCode(topic)
                if item_brains:
                    #if the topic is a glossary element, the list is not empty
                    #this list should contain only one object if the id is unique
                    glossary_item = item_brains[0].getObject()
                else:
                    #the topic is a glossary folder
                    glossary_item = getattr(glossary, topic)
                topic_title = glossary_item.get_translation_by_language(default_lang_name)
                filters['topics'] = topic_title
            except AttributeError:
                #an invalid topic was passed
                return None
        if filter_name is not None:
            filters['title'] = '*%s*' % filter_name

        catalog = self.getCatalogTool()
        if objects:
            items = [ catalog.getobject(ob.data_record_id_)
                     for ob in catalog.search(filters) ]
            return sorted(items, key=lambda ob: ob.title.strip().lower())
        else:
            return catalog.search(filters)

from Products.Naaya.NySite import NySite
NySite.organisations_list = OrganisationLister('organisations_list')

#manage_addNyOrganisation_html = PageTemplateFile('zpt/organisation_manage_add', globals())
#manage_addNyOrganisation_html.kind = config['meta_type']
#manage_addNyOrganisation_html.action = 'addNyOrganisation'
config.update({
    #'constructors': (manage_addNyOrganisation_html, addNyOrganisation),
    'constructors': (organisation_add_html, addNyOrganisation),
    'folder_constructors': [
            # NyFolder.manage_addNyOrganisation_html = manage_addNyOrganisation_html
            #('manage_addNyOrganisation_html', manage_addNyOrganisation_html),
            ('organisation_add_html', organisation_add_html),
            ('addNyOrganisation', addNyOrganisation),
            ('import_organisation_item', importNyOrganisation),
        ],
    'add_method': addNyOrganisation,
    'validation': issubclass(NyOrganisation, NyValidation),
    '_class': NyOrganisation,
})

def get_config():
    return config
