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
from datetime import datetime
from naaya.content.expert.expert_item import METATYPE_OBJECT
import re
from cStringIO import StringIO
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


METATYPE_OBJECT = 'Naaya Institution'
ADDITIONAL_STYLE = open(ImageFile('www/institution.css', globals()).path).read()


DEFAULT_SCHEMA = {}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'webpage': dict(sortorder=120, widget_type='String', label='Webpage'),
    'phone': dict(sortorder=140, widget_type='String', label='Phone'),
    'fax': dict(sortorder=160, widget_type='String', label='Fax'),
    'main_topics': dict(sortorder=200, widget_type='SelectMultiple', label='Main topics covered', list_id='institution_topics'),
    'sub_topics': dict(sortorder=220, widget_type='SelectMultiple', label='Secondary topics covered', list_id='institution_topics'),
    'coverage': dict(sortorder=30, widget_type='Glossary', label='Geographical coverage', glossary_id='coverage', localized=True, visible=False),
    'keywords': dict(sortorder=40, widget_type='Glossary', label='Keywords', glossary_id='keywords', localized=True, visible=False),
    'sortorder': dict(sortorder=50, widget_type='String', data_type='int', default='100', label='Sort order', required=False, visible=False),
    'releasedate': dict(sortorder=60, widget_type='Date', data_type='date', label='Release date', required=False, visible=False),
    'discussion': dict(sortorder=70, widget_type='Checkbox', data_type='int', label='Open for comments', visible=False),
    'geo_location': dict(sortorder=24, widget_type='Geo', data_type='geo', label='Geographical location', visible=True)
})

def setupContentType(site):
    #@TODO: initialize the list of topics (only and only once per site)
    from skel import TOPICS
    ptool = site.getPortletsTool()
    itopics = getattr(ptool, 'institution_topics', None)
    if not itopics:
        ptool.manage_addRefList('institution_topics')
        for k, v in TOPICS.items():
            ptool.institution_topics.manage_add_item(k, v)

    #Create catalog index if it doesn't exist
    ctool = site.getCatalogTool()
    try: 
        ctool.addIndex('topics', 'KeywordIndex', extra={'indexed_attrs' : 'main_topics, sub_topics'})
        ctool.manage_reindexIndex(['topics'])
    except: pass


# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'institution_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': 'Institution',
        'permission': 'Naaya - Add Naaya Institution objects',
        'forms': ['institution_add', 'institution_edit', 'institution_index'],
        'add_form': 'institution_add_html',
        'description': 'This is Naaya Institution type.',
        'properties': {}, #TODO: REMOVE
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyInstitution',
        '_module': sys.modules[__name__],
        'additional_style': ADDITIONAL_STYLE,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInstitution.gif'),
        'on_install' : setupContentType,
        '_misc': {
                'NyInstitution.gif': ImageFile('www/NyInstitution.gif', globals()),
                'NyInstitution_marked.gif': ImageFile('www/NyInstitution_marked.gif', globals()),
            },
    }

def institution_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyInstitution', 'form_helper': form_helper}, 'institution_add')

def _create_NyInstitution_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyInstitution(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyInstitution(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an Institution type of object.
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
    _institution_word = schema_raw_data.get('institution_word', '')

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = 'institution' + self.utGenRandomId(5)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyInstitution_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_institution_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/institution_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    #Process uploaded file
    ob.picture = None
    _uploaded_file = schema_raw_data.pop('institution_picture', None)
    if _uploaded_file is not None and _uploaded_file.filename:
        ob.picture = make_blobfile(_uploaded_file,
                           removed=False,
                           timestamp=datetime.utcnow())

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'institution_manage_add' or l_referer.find('institution_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'institution_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyInstitution(self, param, id, attrs, content, properties, discussion, objects):
    """
    @todo: Not implemented 
    """
    raise NotImplementedError


class institution_item(Implicit, NyContentData):
    """ """
    pass

class NyInstitution(institution_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyInstitution.gif'
    icon_marked = 'misc_/NaayaContent/NyInstitution_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        #if not self.hasVersion():
        #    l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += institution_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        institution_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.firstname, self.lastname, self.getLocalProperty('jobtitle', lang)])

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
        self.version = institution_item()
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
        _uploaded_file = schema_raw_data.pop('institution_picture', None)
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
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    #zmi pages
    #security.declareProtected(view_management_screens, 'manage_edit_html')
    #manage_edit_html = PageTemplateFile('zpt/institution_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'institution_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'institution_edit')
    
    def render_picture(self, RESPONSE):
        """ Render institution picture """
        if hasattr(self, 'picture') and self.picture:
                return self.picture.send_data(RESPONSE, as_attachment=False)

    def delete_picture(self, REQUEST=None):
        """ Delete attached institution picture """
        self.picture = None
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/edit_html' % (self.absolute_url()))

    def getTopics(self, category):
        ptool = self.getPortletsTool()
        topics = getattr(ptool, 'institution_topics', None)
        return [topics.get_item(topic) for topic in category if topics.get_collection().has_key(topic)]

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
                if record.institution == self.title:
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

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

InitializeClass(NyInstitution)


#
class InstitutionLister(Implicit, Item):

    _index_template = NaayaPageTemplateFile('zpt/institutions_list', globals(), 'institution')

    """
    Plug into the catalog to retrieve the list of institutions
    Render the list of institutions recorded for this site.
    """
    def __init__(self, id):
        self.id = id


    def index_html(self, REQUEST):
        """ Index page """
        return self._index_template(REQUEST)


    def topic_filters(self):
        """ 
        Return the list of topics and their count of items inside to be displayed from template.
        Example:
        <ul>
            <li>All (12)</li>
            <li>Water management (10)</li>
            <li>Climate change (2)</li>
        </ul>
        @return: List of tuples in format: [(None, intCountAll), (topic_obj1, intCountObj1), (topic_obj2, intCountObj2)...]
        """
        ret = []
        ptool = self.getPortletsTool()
        ctool = self.getCatalogTool()
        ret.append((None, len(self.items_in_topic(ctool))))
        topics = getattr(ptool, 'institution_topics', None)
        for id, value in topics.get_collection().items():
            ret.append((value, len(self.items_in_topic(ctool, id))))
        return ret


    def items_in_topic(self, catalog=None, topic='', filter_name=None, objects=False):
        """
        Find the institutions that have associated a specific topic (either as primary or secondary topic).
        @param topic: The name of the topic to find items in. If None, return all institutions
        @param objects: Return full objects (True) or just the brains (False). Brains are useful to count: i.e. len(brains_arr)
        @return: list of NyInstitution objects if objects=True or list of catalog brains if objects=False.
        """
        dict = {'meta_type' : METATYPE_OBJECT}
        if not catalog:
            catalog = self.getCatalogTool()
        if topic:
            dict['topics'] = topic
        if filter_name:
            dict['title'] = '*%s*' % filter_name
        if objects:
            return [catalog.getobject(ob.data_record_id_) for ob in catalog.search(dict)]
        return catalog.search(dict)

from Products.Naaya.NySite import NySite
NySite.institutions_list = InstitutionLister('institutions_list')

#manage_addNyInstitution_html = PageTemplateFile('zpt/institution_manage_add', globals())
#manage_addNyInstitution_html.kind = config['meta_type']
#manage_addNyInstitution_html.action = 'addNyInstitution'
config.update({
    #'constructors': (manage_addNyInstitution_html, addNyInstitution),
    'constructors': (institution_add_html, addNyInstitution),
    'folder_constructors': [
            # NyFolder.manage_addNyInstitution_html = manage_addNyInstitution_html
            #('manage_addNyInstitution_html', manage_addNyInstitution_html),
            ('institution_add_html', institution_add_html),
            ('addNyInstitution', addNyInstitution),
            ('import_institution_item', importNyInstitution),
        ],
    'add_method': addNyInstitution,
    'validation': issubclass(NyInstitution, NyValidation),
    '_class': NyInstitution,
})

def get_config():
    return config
