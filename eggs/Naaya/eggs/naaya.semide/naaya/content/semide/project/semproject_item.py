import os
import sys
from copy import deepcopy

from Acquisition import Implicit
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile
import zope.event

from naaya.content.base.constants import (MUST_BE_NONEMPTY, MUST_BE_POSITIV_INT,
                                    MUST_BE_DATETIME, MUST_BE_POSITIV_FLOAT)
from Products.NaayaBase.constants import (PERMISSION_EDIT_OBJECTS,
PERMISSION_DELETE_OBJECTS, EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG,
EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG, EXCEPTION_STARTEDVERSION_MSG,
MESSAGE_SAVEDCHANGES)

from Products.NaayaCore.managers.utils import make_id
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyImportExport import NyImportExport
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, \
                                        NY_CONTENT_BASE_SCHEMA
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from naaya.core import submitter

from naaya.content.semide.organisation.semorganisation_item import (
    addNySemOrganisation, semorganisation_add_html,
    importNySemOrganisation, METATYPE_OBJECT as METATYPE_NYSEMORGANISATION)
from naaya.content.semide.funding.semfunding_item import (
    addNySemFunding, semfunding_add_html,
    importNySemFunding, METATYPE_OBJECT as METATYPE_NYSEMFUNDING)
from naaya.content.semide.fieldsite.semfieldsite_item import (
    addNySemFieldSite, semfieldsite_add_html,
    importNySemFieldSite, METATYPE_OBJECT as METATYPE_NYSEMFIELDSITE)
from naaya.content.semide.document.semdocument_item import (
    addNySemDocument, semdocument_add_html,
    importNySemDocument, METATYPE_OBJECT as METATYPE_NYSEMDOCUMENT)

#module constants
METATYPE_OBJECT = 'Naaya Semide Project'
LABEL_OBJECT = 'Project'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Project objects'
OBJECT_FORMS = ['semproject_add', 'semproject_edit', 'semproject_index']
OBJECT_CONSTRUCTORS = ['manage_addNySemProject_html', 'semproject_add_html', 'addNySemProject', 'importNySemProject']
OBJECT_ADD_FORM = 'semproject_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide Project type.'
PREFIX_OBJECT = 'proj'
PROPERTIES_OBJECT = {
    'id':                           (0, '', ''),
    'title':                        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':                  (0, '', ''),
    'coverage':                     (0, '', ''),
    'keywords':                     (0, '', ''),
    'sortorder':                    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':                  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':                   (0, '', ''),
    'acronym':                      (0, '', ''),
    'budget':                       (0, MUST_BE_POSITIV_FLOAT, 'The budget field must contain a number.'),
    'resourceurl':                  (0, '', ''),
    'programme':                    (0, '', ''),
    'objectives':                   (0, '', ''),
    'results':                      (0, '', ''),
    'start_date':                   (0, '', ''),
    'end_date':                     (0, '', ''),
    'pr_number':                    (0, '', ''),
    'subject':                      (0, '', ''),
    'lang':                         (0, '', ''),
}



DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'pr_number':    dict(sortorder=100, widget_type='String', label="Project Number"),
    'subject':      dict(sortorder=110, widget_type='SelectMultiple', label="Subject"),
    'acronym':      dict(sortorder=120, widget_type='String', label="Acronym", localized=True),
    'budget':       dict(sortorder=130, widget_type='String', label="Budget (EUR)", default="0"),
    'programme':    dict(sortorder=140, widget_type='String', label="Programme", localized=True),
    'resourceurl':  dict(sortorder=150, widget_type='String', label="Web site (URL)", default="http://"),
    'objectives':   dict(sortorder=160, widget_type='TextArea', label="Objectives", localized=True, tinymce=True),
    'results':      dict(sortorder=170, widget_type='TextArea', label="Results", localized=True, tinymce=True),
    'start_date':   dict(sortorder=180, widget_type='Date', label="Start date", required=True),
    'end_date':     dict(sortorder=190, widget_type='Date', label="End date"),
})
DEFAULT_SCHEMA['sortorder'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)

config = {
        'product': 'NaayaContent',
        'module': 'NySemProject',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'properties': PROPERTIES_OBJECT,
        'schema_name': 'NySemProject',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySemProject.gif'),
        '_misc': {
                'NySemProject.gif': ImageFile('www/NySemProject.gif', globals()),
                'NySemProject_marked.gif': ImageFile('www/NySemProject_marked.gif', globals()),
            },
    }

manage_addNySemProject_html = PageTemplateFile('zpt/semproject_manage_add', globals())
manage_addNySemProject_html.kind = METATYPE_OBJECT
manage_addNySemProject_html.action = 'addNySemProject'

def semproject_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemProject', 'form_helper': form_helper}, 'semproject_add')

def _create_NySemProject_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NySemProject(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNySemProject(self, id='', contributor=None, REQUEST=None, **kwargs):
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

    ob = _create_NySemProject_object(self, id, contributor)
    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    ob.start_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('start_date', None))
    ob.end_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('end_date', None))

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/semproject_add_html' % self.absolute_url())

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
        if l_referer == 'semproject_manage_add' or l_referer.find('semproject_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer.find('semproject_add_html') != -1:
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/semproject_add_html' % self.absolute_url())
    return ob.getId()

def importNySemProject(self, param, id, attrs, content, properties, discussion, objects):
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
            ob = _create_NySemProject_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
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
        #go on and import sub objects
        for object in objects:
            ob_meta = object.meta_type
            if ob_meta == METATYPE_NYSEMORGANISATION:
                importNySemOrganisation(ob, object.param, object.id, object.attrs, object.content,
                    object.properties, object.discussion, object.objects)
            elif ob_meta == METATYPE_NYSEMFUNDING:
                importNySemFunding(ob, object.param, object.id, object.attrs, object.content,
                    object.properties, object.discussion, object.objects)
            elif ob_meta == METATYPE_NYSEMFIELDSITE:
                importNySemFieldSite(ob, object.param, object.id, object.attrs, object.content,
                    object.properties, object.discussion, object.objects)
            elif ob_meta == METATYPE_NYSEMDOCUMENT:
                importNySemDocument(ob, object.param, object.id, object.attrs, object.content,
                    object.properties, object.discussion, object.objects)

class semproject_item(Implicit, NyContentData):
    """ """
    meta_type = METATYPE_OBJECT

class NySemProject(semproject_item, NyAttributes, NyImportExport, NyContainer, NyCheckControl, NyContentType, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemProject.py'
    icon_marked = 'misc_/NaayaContent/NySemProject_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],)
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options = l_options + ({'label': 'View', 'action': 'index_html'},) + NyImportExport.manage_options + NyContainer.manage_options[3:8]
        return l_options

    meta_types = (
        {'name': METATYPE_NYSEMORGANISATION, 'action': 'manage_addNySemOrganisation_html'},
        {'name': METATYPE_NYSEMFUNDING, 'action': 'manage_addNySemFunding_html'},
        {'name': METATYPE_NYSEMFIELDSITE, 'action': 'manage_addNySemFieldSite_html'},
        {'name': METATYPE_NYSEMDOCUMENT, 'action': 'manage_addNySemDocument_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    #constructors
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNySemOrganisation')
    addNySemOrganisation = addNySemOrganisation
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'semorganisation_add_html')
    semorganisation_add_html = semorganisation_add_html

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNySemFunding')
    addNySemFunding = addNySemFunding
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'semfunding_add_html')
    semfunding_add_html = semfunding_add_html

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNySemFieldSite')
    addNySemFieldSite = addNySemFieldSite
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'semfieldsite_add_html')
    semfieldsite_add_html = semfieldsite_add_html

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNySemDocument')
    addNySemDocument = addNySemDocument
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'semdocument_add_html')
    semdocument_add_html = semdocument_add_html

    def __init__(self, id, contributor):
        """ """
        self.id = id
        semproject_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        self.contributor = contributor

    def __getattr__(self, name):
        """
        Called when an attribute lookup has not found the attribute in the usual places.
        @param name: the attribute name
        @return: should return the attribute value or raise an I{AttributeError} exception.
        """
        if name.startswith('objectkeywords_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.objectkeywords(lang)
        elif name.startswith('istranslated_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.istranslated(lang)
        elif name.startswith('coverage_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.getLocalProperty('coverage', lang)
        elif name.startswith('programme_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.getLocalProperty('programme', lang)
        else:
            return super(NySemProject, self).__getattr__(name)

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(self.subject)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('acronym', lang),
            self.getLocalProperty('programme', lang), self.getLocalProperty('objectives', lang),
            self.getLocalProperty('results', lang)])

    def exportdata_custom(self, all_levels=1):
        # exports all the Naaya content in XML format from this project
        return self.export_this(all_levels=all_levels)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'budget="%s" resourceurl="%s" start_date="%s" end_date="%s" pr_number="%s" subject="%s"' % \
               (self.utXmlEncode(self.budget),
                self.utXmlEncode(self.resourceurl),
                self.utXmlEncode(self.utNoneToEmpty(self.start_date)),
                self.utXmlEncode(self.utNoneToEmpty(self.end_date)),
                self.utXmlEncode(self.pr_number),
                self.utXmlEncode(self.subject))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<acronym lang="%s"><![CDATA[%s]]></acronym>' % (l, self.utToUtf8(self.getLocalProperty('acronym', l))))
            ra('<programme lang="%s"><![CDATA[%s]]></programme>' % (l, self.utToUtf8(self.getLocalProperty('programme', l))))
            ra('<objectives lang="%s"><![CDATA[%s]]></objectives>' % (l, self.utToUtf8(self.getLocalProperty('objectives', l))))
            ra('<results lang="%s"><![CDATA[%s]]></results>' % (l, self.utToUtf8(self.getLocalProperty('results', l))))
        for x in self.getFundings():
            ra(x.export_this())
        for x in self.getDocuments():
            ra(x.export_this())
        for x in self.getOrganisations():
            ra(x.export_this())
        for x in self.getFieldSites():
            ra(x.export_this())

        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>%s</dc:format>' % self.utXmlEncode(self.format()))
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        for k in self.subject:
            if k:
                theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
                theme_name = theme_ob.theme_name
                if theme_name:
                    ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(theme_name.strip()))

        ra('<ut:ID>%s</ut:ID>' % self.utXmlEncode(self.id))
        ra('<ut:Acronym>%s</ut:Acronym>' % self.utXmlEncode(self.getLocalProperty('acronym', lang)))
        ra('<ut:Title>%s</ut:Title>' % self.utXmlEncode(self.getLocalProperty('title', lang)))
        ra('<ut:Budget_Total Currency="EUR">%s</ut:Budget_Total>' % self.utXmlEncode(self.budget))
        for k in self.getLocalProperty('keywords', lang).split(','):
            ra('<ut:keywords>%s</ut:keywords>' % self.utXmlEncode(k))
        for fund_item in self.getFundings():
            ra('<ut:Funding>')
            ra('<ut:Source>%s</ut:Source>' % self.utXmlEncode(fund_item.getLocalProperty('funding_source', lang)))
            ra('<ut:Programme>%s</ut:Programme>' % self.utXmlEncode(fund_item.getLocalProperty('funding_programme', lang)))
            ra('<ut:Type>%s</ut:Type>' % self.utXmlEncode(fund_item.getLocalProperty('funding_type', lang)))
            ra('<ut:Funding_Rate>%s</ut:Funding_Rate>' % self.utXmlEncode(fund_item.getLocalProperty('funding_rate', lang)))
            ra('</ut:Funding>')
        ra('<ut:Programme_Field>%s</ut:Programme_Field>' % self.utXmlEncode(self.getLocalProperty('programme', lang)))
        ra('<ut:Source>%s</ut:Source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<ut:WebSite>%s</ut:WebSite>' % self.utXmlEncode(self.resourceurl))
        ra('<ut:Background><![CDATA[%s]]></ut:Background>' % self.utXmlEncode(self.getLocalProperty('description', lang)))
        ra('<ut:Objectives><![CDATA[%s]]></ut:Objectives>' % self.utXmlEncode(self.getLocalProperty('objectives', lang)))
        ra('<ut:Results><![CDATA[%s]]></ut:Results>' % self.utXmlEncode(self.getLocalProperty('results', lang)))
        ra('<ut:Starting_Date>%s</ut:Starting_Date>' % self.utShowFullDateTimeHTML(self.start_date))
        ra('<ut:Ending_Date>%s</ut:Ending_Date>' % self.utShowFullDateTimeHTML(self.end_date))
        for doc_item in self.getDocuments():
            ra('<ut:Document>')
            ra('<dc:title>%s</dc:title>' % self.utXmlEncode(doc_item.getLocalProperty('title', lang)))
            ra('<dc:file_link>%s</dc:file_link>' % self.utXmlEncode(doc_item.getLocalProperty('file_link', lang)))
            ra('<ut:type_document>%s</ut:type_document>' % self.utXmlEncode(doc_item.document_type))
            ra('</ut:Document>')
        for org_item in self.getOrganisations():
            ra('<ut:Partners>')
            #TODO: the acronym property was not specified
            ra('<ut:Or_Name Or_Acronym="%s">%s</ut:Or_Name>' % ('acronym', self.utXmlEncode(org_item.getLocalProperty('results', lang))))
            ra('<ut:Or_Type>%s</ut:Or_Type>' % self.utXmlEncode(org_item.org_type))
            ra('<ut:Or_Desc>%s</ut:Or_Desc>' % self.utXmlEncode(org_item.getLocalProperty('description', lang)))
            ra('<ut:Or_address>%s</ut:Or_address>' % self.utXmlEncode(org_item.getLocalProperty('address', lang)))
            for k in self.splitToList(org_item.getLocalProperty('coverage', lang)):
                ra('<ut:Or_Country>%s</ut:Or_Country>' % self.utXmlEncode(k))
            ra('<ut:Or_WebSite>%s</ut:Or_WebSite>' % self.utXmlEncode(org_item.org_url))
            #TODO: explain the coordinator attribute
            #TODO: contacts must be a list
            ra('<ut:Or_Contact Coordinator="0">')
            #TODO: explain attribute 'Project_Manager'
            ra('<ut:Co_Title>%s</ut:Co_Title>' % self.utXmlEncode(org_item.getLocalProperty('contact_title', lang)))
            ra('<ut:Co_FirstName>%s</ut:Co_FirstName>' % self.utXmlEncode(org_item.getLocalProperty('contact_firstname', lang)))
            ra('<ut:Co_LastName>%s</ut:Co_LastName>' % self.utXmlEncode(org_item.getLocalProperty('contact_lastname', lang)))
            ra('<ut:Co_Position>%s</ut:Co_Position>' % self.utXmlEncode(org_item.getLocalProperty('contact_position', lang)))
            ra('<ut:Co_Email>%s</ut:Co_Email>' % self.utXmlEncode(org_item.contact_email))
            ra('<ut:Co_Tel>%s</ut:Co_Tel>' % self.utXmlEncode(org_item.contact_phone))
            ra('<ut:Co_Fax>%s</ut:Co_Fax>' % self.utXmlEncode(org_item.contact_fax))
            ra('</ut:Or_Contact>')
            ra('</ut:Partners>')
        for fs_item in self.getFieldSites():
            ra('<ut:Field_sites>')
            ra('<ut:Site_name>%s</ut:Site_name>' % self.utXmlEncode(fs_item.getLocalProperty('title', lang)))
            ra('<ut:Site_country>%s</ut:Site_country>' % self.utXmlEncode(fs_item.getLocalProperty('coverage', lang)))
            for k in self.splitToList(fs_item.getLocalProperty('fieldsite_rb', lang)):
                ra('<ut:River_basin>%s</ut:River_basin>' % self.utXmlEncode(k))
            ra('</ut:Field_sites>')
        ra(self.syndicateThisFooter())
        return ''.join(r)

    def getOrganisations(self): return self.objectValues(METATYPE_NYSEMORGANISATION)
    def getFundings(self):      return self.objectValues(METATYPE_NYSEMFUNDING)
    def getFieldSites(self):    return self.objectValues(METATYPE_NYSEMFIELDSITE)
    def getDocuments(self):     return self.objectValues(METATYPE_NYSEMDOCUMENT)

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

        self.start_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('start_date', None))
        self.end_date = self.utConvertStringToDateTimeObj(schema_raw_data.get('end_date', None))

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
        self.version = semproject_item()
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
    manage_edit_html = PageTemplateFile('zpt/semproject_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semproject_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semproject_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semproject_edit')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrorsTrans('Error while delete data.')
        else: self.setSessionInfoTrans('Item(s) deleted.')
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

#Custom folder listing
NaayaPageTemplateFile('zpt/semproject_folder_index', globals(),
                      'semproject_folder_index')

InitializeClass(NySemProject)

config.update({
    'constructors': (manage_addNySemProject_html, addNySemProject),
    'folder_constructors': [
            ('manage_addNySemProject_html', manage_addNySemProject_html),
            ('semproject_add_html', semproject_add_html),
            ('addNySemProject', addNySemProject),
            ('import_NySemProject', importNySemProject),
        ],
    'add_method': addNySemProject,
    'validation': issubclass(NySemProject, NyValidation),
    '_class': NySemProject,
})

def get_config():
    return config
