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
# Lehel Kacso, Finsiel Romania

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
from reportsection_item                 import reportsection_item

from Products.NaayaContent.NyReportQuestion.NyReportQuestion       import addNyReportQuestion, reportquestion_add_html, manage_addNyReportQuestion_html
from Products.NaayaContent.NyReportQuestion.NyReportQuestion       import METATYPE_OBJECT as METATYPE_NYREPORTQUESTION

from Products.NaayaContent.NyReportQuestionnaire.NyReportQuestionnaire       import addNyReportQuestionnaire, reportquestionnaire_add_html, manage_addNyReportQuestionnaire_html
from Products.NaayaContent.NyReportQuestionnaire.NyReportQuestionnaire       import METATYPE_OBJECT as METATYPE_NYREPORTQUESTIONNAIRE

#module constants
METATYPE_OBJECT = 'Naaya Report Section'
LABEL_OBJECT = 'Report Section'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Report Section objects'
OBJECT_FORMS = ['reportsection_add', 'reportsection_edit', 'reportsection_index']
OBJECT_CONSTRUCTORS = ['manage_addNyReportSection_html', 'reportsection_add_html', 'addNyReportSection', 'importNyReportSection']
OBJECT_ADD_FORM = 'reportsection_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Report Section type.'
PREFIX_OBJECT = 'sec'
PROPERTIES_OBJECT = {
    'id':                           (0, '', ''),
    'title':                        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':                  (0, '', ''),
    'coverage':                     (0, '', ''),
    'keywords':                     (0, '', ''),
    'sortorder':                    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':                  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':                   (0, '', ''),
    'lang':                         (0, '', '')
}

manage_addNyReportSection_html = PageTemplateFile('zpt/reportsection_manage_add', globals())
manage_addNyReportSection_html.kind = METATYPE_OBJECT
manage_addNyReportSection_html.action = 'addNyReportSection'

def reportsection_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyReportSection'}, 'reportsection_add')

def addNyReportSection(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Report Section type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'manage_addNyReportSection_html' or l_referer.find('manage_addNyReportSection_html') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #create object
        ob = NyReportSection(id, title, description, coverage, keywords, sortorder, contributor, releasedate, lang)
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
            if l_referer == 'manage_addNyReportSection_html' or l_referer.find('manage_addNyReportSection_html') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'reportsection_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, lang=lang)
            REQUEST.RESPONSE.redirect('%s/reportsection_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNyReportSection(self, param, id, attrs, content, properties, discussion, objects):
    pass
    #TODO: to be added
#    #this method is called during the import process
#    try: param = abs(int(param))
#    except: param = 0
#    if param == 3:
#        #just try to delete the object
#        try: self.manage_delObjects([id])
#        except: pass
#    else:
#        ob = self._getOb(id, None)
#        if param in [0, 1] or (param==2 and ob is None):
#            if param == 1:
#                #delete the object if exists
#                try: self.manage_delObjects([id])
#                except: pass
#            addNyReportSection(self, id=id,
#                sortorder=attrs['sortorder'].encode('utf-8'),
#                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
#                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
#            ob = self._getOb(id)
#            for property, langs in properties.items():
#                for lang in langs:
#                    ob._setLocalPropValue(property, lang, langs[lang])
#            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
#                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
#            if attrs['releasedate'].encode('utf-8') != '':
#                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
#            ob.submitThis()
#            ob.import_comments(discussion)
#            self.recatalogNyObject(ob)

class NyReportSection(NyAttributes, reportsection_item, NyContainer, NyEpozToolbox, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyReportSection.gif'
    icon_marked = 'misc_/NaayaContent/NyReportSection_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],) + reportsection_item.manage_options
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    def all_meta_types(self, interfaces=None):
        """ """
        y = [{'name': METATYPE_OBJECT, 'action': 'manage_addNyReportSection_html'},
            {'name': METATYPE_NYREPORTQUESTION, 'action': 'manage_addNyReportQuestion_html'},
            {'name': METATYPE_NYREPORTQUESTIONNAIRE, 'action': 'manage_addNyReportQuestionnaire_html'}]
        additional_meta_types = ['File', 'Image']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    #constructors
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNyReportSection')
    addNyReportSection = addNyReportSection
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'reportsection_add_html')
    reportsection_add_html = reportsection_add_html

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNyReportQuestion')
    addNyReportQuestion = addNyReportQuestion
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'reportquestion_add_html')
    reportquestion_add_html = reportquestion_add_html

    security.declareProtected('Naaya - Add comments for content', 'addNyReportQuestionnaire')
    addNyReportQuestionnaire = addNyReportQuestionnaire
    security.declareProtected('Naaya - Add comments for content', 'reportquestionnaire_add_html')
    reportquestionnaire_add_html = reportquestionnaire_add_html

    def __init__(self, id, title, description, coverage, keywords, sortorder, contributor, releasedate, lang):
        """ """
        self.id = id
        reportsection_item.__dict__['__init__'](self,title, description, coverage, keywords, sortorder, releasedate, lang)
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
        raise AttributeError, name

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang)])

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        pass

    def getSections(self): return self.utSortObjsListByAttr(self.objectValues(METATYPE_OBJECT),'sortorder',0)
    def getQuestions(self): return self.utSortObjsListByAttr(self.objectValues(METATYPE_NYREPORTQUESTION),'sortorder',0)
    def getQuestionsLocation(self):
        if self.hasQuestions(): return self
        else:                   return self.getParentNode().getQuestionsLocation()
    def hasQuestions(self):
        return len(self.getQuestions()) > 0

    def getQuestionnaires(self): return self.utSortObjsListByAttr(self.objectValues(METATYPE_NYREPORTQUESTIONNAIRE),'sortorder',0)
    def hasQuestionnaires(self):
        return len(self.getQuestionnaires()) > 0

    def getQuestionIds(self):
        obs = self.objectValues(METATYPE_NYREPORTQUESTION)
        obs = self.utSortObjsListByAttr(obs,'sortorder',0)
        return [ob.id for ob in obs]
    def getQuestionById(self,p_id):
        return self._getOb(p_id)

    def getRateValue(self, qnr, rate):
        """ """
        try:
            return qnr.ratings[rate.title]
        except:
            return None

    def getNavigationInfo(self):
        l_up = self.getParentNode()
        siblings = l_up.getSections()
        l_prev = None
        l_next = None
        l_temp = None
        for obj in siblings:
            if(obj==self): l_prev = l_temp
            if(l_temp==self): l_next = obj
            l_temp = obj;
        return [l_prev, l_up, l_next]

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', approved='', releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, releasedate, lang)
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
        self.releasedate =  self.version.releasedate
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
        self.version = reportsection_item(self.title, self.description, self.coverage,
            self.keywords, self.sortorder, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder,
                    releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, releasedate, lang)
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
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declareProtected(view, 'toc')
    def toc(self):
        """ return the table of contents """
        return self.getChapterPath()

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/reportsection_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportsection_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportsection_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportsection_edit')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'reportquestions_html')
    def reportquestions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportquestions_index')

    security.declareProtected(view, 'reportquestionnaires_html')
    def reportquestionnaires_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportquestionnaires_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'questionnaire_edit_html')
    def questionnaire_edit_html(self, qnr='', REQUEST=None, RESPONSE=None):
        """ """
        qnr_ob = self.unrestrictedTraverse(qnr, '')
        if qnr_ob:
            return self.getFormsTool().getContent({'here': self, 'qnr': qnr_ob}, 'reportquestionnaire_edit')
        else:
            self.setSessionErrors(['Bad questionnaire ID.'])
            REQUEST.RESPONSE.redirect('reportquestionnaires_html')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'questionnaire_rate_html')
    def questionnaire_rate_html(self, qnr='', REQUEST=None, RESPONSE=None):
        """ """
        qnr_ob = self.unrestrictedTraverse(qnr, '')
        if qnr_ob:
            return self.getFormsTool().getContent({'here': self, 'qnr': qnr_ob}, 'reportquestionnaire_rate')
        else:
            self.setSessionErrors(['Bad questionnaire ID.'])
            REQUEST.RESPONSE.redirect('reportquestionnaires_html')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'delete_questionnaire')
    def delete_questionnaire(self, qnr, REQUEST=None, RESPONSE=None):
        """ """
        try:
            self.manage_delObjects(qnr)
            self.setSessionInfo(['Questionnaire deleted.'])
        except:
            self.setSessionErrors(['Error while delete data.'])
        if REQUEST: REQUEST.RESPONSE.redirect('reportquestionnaires_html')

    security.declareProtected(view, 'report_macro_objecttree_html')
    def report_macro_objecttree_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().report_macro_objecttree

InitializeClass(NyReportSection)
