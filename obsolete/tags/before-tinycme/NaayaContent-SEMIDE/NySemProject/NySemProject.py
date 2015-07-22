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

#Python imports
from copy import deepcopy

#Zope imports
from Globals                                    import InitializeClass
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
import Products

#Product imports
from Products.NaayaContent.constants    import *
from Products.NaayaBase.constants       import *
from Products.NaayaBase.NyContainer     import NyContainer
from Products.NaayaBase.NyAttributes    import NyAttributes
from Products.NaayaBase.NyEpozToolbox   import NyEpozToolbox
from Products.NaayaBase.NyCheckControl  import NyCheckControl
from semproject_item                    import semproject_item

from Products.NaayaContent.NySemOrganisation.NySemOrganisation  import addNySemOrganisation, semorganisation_add_html, manage_addNySemOrganisation_html, importNySemOrganisation
from Products.NaayaContent.NySemOrganisation.NySemOrganisation  import METATYPE_OBJECT as METATYPE_NYSEMORGANISATION
from Products.NaayaContent.NySemFunding.NySemFunding            import addNySemFunding, semfunding_add_html, manage_addNySemFunding_html, importNySemFunding
from Products.NaayaContent.NySemFunding.NySemFunding            import METATYPE_OBJECT as METATYPE_NYSEMFUNDING
from Products.NaayaContent.NySemFieldSite.NySemFieldSite        import addNySemFieldSite, semfieldsite_add_html, manage_addNySemFieldSite_html, importNySemFieldSite
from Products.NaayaContent.NySemFieldSite.NySemFieldSite        import METATYPE_OBJECT as METATYPE_NYSEMFIELDSITE
from Products.NaayaContent.NySemDocument.NySemDocument          import addNySemDocument, semdocument_add_html, manage_addNySemDocument_html, importNySemDocument
from Products.NaayaContent.NySemDocument.NySemDocument          import METATYPE_OBJECT as METATYPE_NYSEMDOCUMENT

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
    'start_date':                   (1, MUST_BE_DATETIME_STRICT, 'The start date field must contain a valid date.'),
    'end_date':                     (0, MUST_BE_DATETIME, 'The end date field must contain a valid date.'),
    'lang':                         (0, '', ''),
    'pr_number':                    (0, '', ''),
    'subject':                      (0, '', '')
}

manage_addNySemProject_html = PageTemplateFile('zpt/semproject_manage_add', globals())
manage_addNySemProject_html.kind = METATYPE_OBJECT
manage_addNySemProject_html.action = 'addNySemProject'

def semproject_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemProject'}, 'semproject_add')

def addNySemProject(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', acronym='', budget='', resourceurl='', programme='',
    objectives='', results='', start_date='', end_date='',
    contributor=None, releasedate='', discussion='', lang=None, pr_number='', subject='', REQUEST=None, **kwargs):
    """
    Create a Project type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'semproject_manage_add' or l_referer.find('semproject_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            acronym=acronym, budget=budget, resourceurl=resourceurl, \
            programme=programme, objectives=objectives, results=results, \
            start_date=start_date, end_date=end_date, pr_number=pr_number, subject=subject)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        releasedate = self.process_releasedate(releasedate)
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #create object
        ob = NySemProject(id, title, description, coverage, keywords, sortorder, acronym,
            budget, programme, resourceurl, objectives, results, start_date,
            end_date, contributor, releasedate, lang, pr_number, subject)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'semproject_manage_add' or l_referer.find('semproject_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'semproject_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                acronym=acronym, budget=budget, resourceurl=resourceurl, \
                programme=programme, \
                objectives=objectives, results=results, start_date=start_date, end_date=end_date, \
                lang=lang, pr_number=pr_number, subject=subject)
            REQUEST.RESPONSE.redirect('%s/semproject_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

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
            addNySemProject(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                budget=attrs['budget'].encode('utf-8'),
                pr_number=attrs['pr_number'].encode('utf-8'),
                subject=eval(attrs['subject'].encode('utf-8')),
                resourceurl=attrs['resourceurl'].encode('utf-8'),
                start_date=self.utConvertDateTimeObjToString(self.utGetDate(attrs['start_date'].encode('utf-8'))),
                end_date=self.utConvertDateTimeObjToString(self.utGetDate(attrs['end_date'].encode('utf-8'))),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
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


class NySemProject(NyAttributes, semproject_item, NyContainer, NyEpozToolbox, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemProject.py'
    icon_marked = 'misc_/NaayaContent/NySemProject_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],) + semproject_item.manage_options
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
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

    def __init__(self, id, title, description, coverage, keywords, sortorder, acronym,
        budget, programme, resourceurl, objectives, results, start_date,
        end_date, contributor, releasedate, lang, pr_number, subject):
        """ """
        self.id = id
        semproject_item.__dict__['__init__'](self,title, description, coverage,
            keywords, sortorder, acronym, budget,programme, resourceurl, objectives,
            results, start_date, end_date, releasedate, lang, pr_number, subject)
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
        raise AttributeError, name

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(self.subject)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('acronym', lang),
            self.getLocalProperty('programme', lang), self.getLocalProperty('objectives', lang),
            self.getLocalProperty('results', lang)])

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
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', approved='', acronym='', budget='', resourceurl='',
        programme='', objectives='', results='', start_date='', end_date='',
        releasedate='', discussion='', lang='', pr_number='', subject='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        subject = self.utConvertToList(subject)
        if approved: approved = 1
        else: approved = 0
        start_date = self.utConvertStringToDateTimeObj(start_date)
        end_date = self.utConvertStringToDateTimeObj(end_date)
        releasedate = self.process_releasedate(releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, acronym,
            budget, programme, resourceurl, objectives, results, start_date,
            end_date, releasedate, lang, pr_number, subject)
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
        self._p_changed = 1
        if discussion: self.open_for_comments()
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
        self._local_properties_metadata = deepcopy(self.version._local_properties_metadata)
        self._local_properties = deepcopy(self.version._local_properties)
        self.sortorder =    self.version.sortorder
        self.budget =       self.version.budget
        self.resourceurl =  self.version.resourceurl
        self.start_date =   self.version.start_date
        self.end_date =     self.version.end_date
        self.releasedate =  self.version.releasedate
        self.pr_number =    self.version.pr_number
        self.subject =      self.version.subject
        self.setProperties(deepcopy(self.version.getProperties()))
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
        self.version = semproject_item(self.title, self.description, self.coverage,
            self.keywords, self.sortorder, self.acronym, self.budget,
            self.programme, self.resourceurl, self.objectives, self.results, self.start_date,
            self.end_date, self.releasedate, self.gl_get_selected_language(), self.pr_number, self.subject)
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', acronym='', budget='', resourceurl='',
        programme='', objectives='', results='', start_date='', end_date='',
        releasedate='', discussion='', lang=None, pr_number='', subject='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            acronym=acronym, budget=budget, resourceurl=resourceurl, \
            programme=programme, objectives=objectives, results=results, \
            start_date=start_date, end_date=end_date, pr_number=pr_number, subject=subject)
        if not len(r):
            sortorder = int(sortorder)
            start_date = self.utConvertStringToDateTimeObj(start_date)
            end_date = self.utConvertStringToDateTimeObj(end_date)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, acronym,
                    budget, programme, resourceurl, objectives, results, start_date,
                    end_date, releasedate, lang, pr_number, subject)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, acronym,
                    budget, programme, resourceurl, objectives, results, start_date,
                    end_date, releasedate, lang, pr_number, subject)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    acronym=acronym, budget=budget, resourceurl=resourceurl, \
                    programme=programme, objectives=objectives, results=results, \
                    start_date=start_date, end_date=end_date, pr_number=pr_number, subject=subject)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

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
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

InitializeClass(NySemProject)
