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
from reportquestionnaire_item           import reportquestionnaire_item
from Products.NaayaContent.NyReportAnswer.NyReportAnswer       import addNyReportAnswer, reportanswer_add_html, manage_addNyReportAnswer_html
from Products.NaayaContent.NyFile.NyFile       import addNyFile, manage_addNyFile_html
from Products.NaayaContent.NyFile.NyFile import METATYPE_OBJECT as METATYPE_NYFILE
from Products.NaayaContent.NyReportAnswer.NyReportAnswer       import METATYPE_OBJECT as METATYPE_NYREPORTANSWER
from Products.NaayaContent.NyReportComment.NyReportComment     import addNyReportComment, reportcomment_add_html, manage_addNyReportComment_html
from Products.NaayaContent.NyReportComment.NyReportComment     import METATYPE_OBJECT as METATYPE_NYREPORTCOMMENT

#module constants
METATYPE_OBJECT = 'Naaya Report Questionnaire'
LABEL_OBJECT = 'Report Questionnaire'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Report Questionnaire objects'
OBJECT_FORMS = ['reportquestionnaire_add', 'reportquestionnaire_edit', 'reportquestionnaire_index', 'reportquestionnaires_index', 'reportquestionnaire_rate']
OBJECT_CONSTRUCTORS = ['manage_addNyReportQuestionnaire_html', 'reportquestionnaire_add_html', 'addNyReportQuestionnaire', 'importNyReportQuestionnaire']
OBJECT_ADD_FORM = 'reportquestionnaire_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Report Questionnaire type.'
PREFIX_OBJECT = 'qre'
PROPERTIES_OBJECT = {
    'id':                           (0, '', ''),
    'title':                        (0, '', ''),
    'description':                  (0, '', ''),
    'coverage':                     (0, '', ''),
    'keywords':                     (0, '', ''),
    'sortorder':                    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':                  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':                   (0, '', ''),
    'qauthor':                      (0, '', ''),
    'answers':                      (0, '', ''),
    'lang':                         (0, '', ''),
}


manage_addNyReportQuestionnaire_html = PageTemplateFile('zpt/reportquestionnaire_manage_add', globals())
manage_addNyReportQuestionnaire_html.kind = METATYPE_OBJECT
manage_addNyReportQuestionnaire_html.action = 'addNyReportQuestionnaire'

def reportquestionnaire_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyReportQuestionnaire'}, 'reportquestionnaire_add')

def addNyReportQuestionnaire(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', contributor=None, releasedate='', discussion='', qauthor='', answers={}, files=None, file_title='', adt_comment=[], REQUEST=None, **kwargs):
    """
    Create a Report Questionnaire type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    answers = {}
    if len(self.getQuestionIds()) > 0:
        for q in self.getQuestionIds():
            answers[q] = REQUEST[q]
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'manage_addNyReportQuestionnaire_html' or l_referer.find('manage_addNyReportQuestionnaire_html') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, qauthor=qauthor, answers=answers, adt_comment=adt_comment)
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
        lang = self.gl_get_selected_language()
        #create object
        ob = NyReportQuestionnaire(id, title, description, coverage, keywords, sortorder, contributor, releasedate, qauthor, answers, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        file_ob = ob.process_nyfile_upload(files, file_title, lang)
        if file_ob:
            for portal_lang in self.gl_get_languages_map():
                if portal_lang['id'] != lang:
                    file_ob._setLocalPropValue('title', portal_lang['id'], self.translate_comment(file_title, lang, portal_lang['id']))
        ob.updatePropertiesFromGlossary(lang)
        #set automatic translation
        for portal_lang in self.gl_get_languages_map():
            if portal_lang['id'] != lang:
                res_answers = {}
                for k, v in answers.items():
                    ob.addNyReportAnswer(answer=v, assoc_question=k)
                    answer_ob = ob.getAnswerByQuestion(k)
                    answer_ob._setLocalPropValue('answer', portal_lang['id'], self.translate_comment(v, lang, portal_lang['id']))
                for com in adt_comment:
                    com_id = self.generateItemId('com')
                    ob.addNyReportComment(id=com_id, page=com['page'], line=com['line'], comment=com['comment'])
                    com_ob = ob.getCommentById(com_id)
                    com_ob._setLocalPropValue('comment', portal_lang['id'], self.translate_comment(com['comment'], lang, portal_lang['id']))
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        #self.notifyFolderMaintainer(self, ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'manage_addNyReportQuestionnaire_html' or l_referer.find('manage_addNyReportQuestionnaire_html') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'reportquestionnaire_add_html':
                self.setSession('referer', self.absolute_url())
                self.setSession('answers', 1)
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, qauthor=qauthor, answers=answers, lang=lang, adt_comment=adt_comment)
            REQUEST.RESPONSE.redirect('%s/reportquestionnaire_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNyReportQuestionnaire(self, param, id, attrs, content, properties, discussion, objects):
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
#            addNyReportQuestionnaire(self, id=id,
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

class NyReportQuestionnaire(NyAttributes, reportquestionnaire_item, NyContainer, NyEpozToolbox, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyReportQuestionnaire.gif'
    icon_marked = 'misc_/NaayaContent/NyReportQuestionnaire_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],) + reportquestionnaire_item.manage_options
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    meta_types = ({'name': METATYPE_NYFILE, 'action': 'manage_addNyFile_html'},
                  {'name': METATYPE_NYREPORTANSWER, 'action': 'manage_addNyReportAnswer_html'},
                  {'name': METATYPE_NYREPORTCOMMENT, 'action': 'manage_addNyReportComment_html'})
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, contributor, releasedate, qauthor, answers, lang):
        """ """
        self.id = id
        reportquestionnaire_item.__dict__['__init__'](self,title, description, coverage, keywords, sortorder, releasedate, qauthor, answers, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        self.contributor = contributor
        self.ratings = {}
        self.votes = 0

    def __setstate__(self,state):
        """Updates"""
        NyReportQuestionnaire.inheritedAttribute("__setstate__") (self, state)
        if not hasattr(self, 'ratings'):
            self.ratings = {}
        if not hasattr(self, 'votes'):
            self.votes = 0

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

    #constructors
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNyReportAnswer')
    addNyReportAnswer = addNyReportAnswer
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'reportanswer_add_html')
    reportanswer_add_html = reportanswer_add_html
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addNyReportComment')
    addNyReportComment = addNyReportComment
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'reportcomment_add_html')
    reportcomment_add_html = reportcomment_add_html

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', approved='', releasedate='', discussion='', qauthor='', answers={}, lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, releasedate, qauthor, answers, lang)
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
        self.answers   =    self.version.answers
        self.qauthor   =    self.version.qauthor
        self.lang   =    self.version.lang
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
        self.version = reportquestionnaire_item(self.title, self.description, self.coverage,
            self.keywords, self.sortorder, self.releasedate, self.qauthor, self.answers, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', contributor=None, releasedate='', discussion='', qauthor='',
        answers={}, lang=None, adt_comment='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.contributor = contributor
        answers = {}
        for q in self.getQuestionIds():
            answers[q] = REQUEST[q]
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
                    releasedate, qauthor, answers, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, releasedate, qauthor, qauthor, answers, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            #set answer
            for portal_lang in self.gl_get_languages_map():
                res_answers = {}
                for k, v in answers.items():
                    try:
                        answer_ob = self.getAnswerByQuestion(k)
                    except:
                        self.addNyReportAnswer(answer=v, assoc_question=k)
                        answer_ob = self.getAnswerByQuestion(k)
                    if portal_lang['id'] == lang:
                        answer_ob._setLocalPropValue('answer', portal_lang['id'], v)
                    else:
                        answer_ob._setLocalPropValue('answer', portal_lang['id'], self.translate_comment(v, lang, portal_lang['id']))
                for com in adt_comment:
                    com_ob = self.getCommentById(com['id'])
                    if portal_lang['id'] == lang:
                        com_ob._setLocalPropValue('comment', portal_lang['id'], com['comment'])
                    else:
                        com_ob._setLocalPropValue('comment', portal_lang['id'], self.translate_comment(com['comment'], lang, portal_lang['id']))

            self._p_changed = 1
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                #REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
                REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, qauthor=qauthor, answers=answers)
                #REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
                REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveRate')
    def saveRate(self, REQUEST=None):
        """ """
        stat_tool = self.getStatisticsTool()
        rate_lists = stat_tool.getRateLists()
        for r in rate_lists:
            if REQUEST.has_key(r.id):
                self.ratings[r.title] = REQUEST[r.id]
                self.votes += 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/reportquestionnaires_html' % self.aq_parent.absolute_url())

    security.declareProtected(view, 'getRatings')
    def getRatings(self):
        output = {}
        stat_tool = self.getStatisticsTool()
        rate_lists = stat_tool.getRateLists()
        if self.votes == 0:
            return None
        else:
            for r in rate_lists:
                procent = 0
                if r.title in self.ratings.keys():
                    try:
                        buf = [o.id for o in r.get_list()]
                        val = buf.index(self.ratings[r.title]) + 1
                        procent = val*100/len(r.get_list())
                    except:
                        return None
                output[r.title] = procent
            return output

    security.declareProtected(view, 'process_nyfile_upload')
    def process_nyfile_upload(self, file='', file_title='', lang='', REQUEST=None):
        """ """
        if file:
            id = 'file' + self.utGenRandomId(6)
            if not file_title: 
                file_title = ' '
            addNyFile(self, id=id, title=file_title, file=file, lang=lang)
            return self._getOb(id)

    #Answers related API
    security.declareProtected(view, 'getAllAnswers')
    def getAllAnswers(self):    return self.objectValues(METATYPE_NYREPORTANSWER)

    security.declareProtected(view, 'getAnswerByQuestion')
    def getAnswerByQuestion(self, question_id):
        """ """
        for k in self.getAllAnswers():
            if str(k.assoc_question) == str(question_id):
                return k

    security.declareProtected(view, 'getFiles')
    def getFiles(self):
        """ """
        return self.objectValues(METATYPE_NYFILE)

    #Comments related API
    security.declareProtected(view, 'getCommentById')
    def getCommentById(self, id):
        """ """
        return getattr(self, id, None)

    security.declareProtected(view, 'getAllComments')
    def getAllComments(self):    return self.objectValues(METATYPE_NYREPORTCOMMENT)

    security.declareProtected(view, 'hasComments')
    def hasComments(self):
        return len(self.getAllComments()) > 0

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/reportquestionnaire_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportquestionnaire_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportquestionnaire_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportquestionnaire_edit')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(view, 'report_macro_objecttree_html')
    def report_macro_objecttree_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().report_macro_objecttree

InitializeClass(NyReportQuestionnaire)