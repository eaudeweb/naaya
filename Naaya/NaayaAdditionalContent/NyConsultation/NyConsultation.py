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
#
# David Batranu, Eau de Web

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from OFS.Image import cookId

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.NaayaContent.NyExFile.NyExFile import addNyExFile
from question_item import question_item
from review_item import addConsultationReviewItem


#module constants
PERMISSION_REVIEW_CONSULTATION = 'Review Consultation'
PERMISSION_MANAGE_CONSULTATION = 'Manage Consultation'

METATYPE_OBJECT = 'Naaya Consultation'
LABEL_OBJECT = 'Consultation'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Consultation objects'
OBJECT_FORMS = ['consultation_add', 'consultation_edit', 'consultation_index']
OBJECT_CONSTRUCTORS = ['manage_addNyConsultation_html', 'consultation_add_html', 'addNyConsultation']
OBJECT_ADD_FORM = 'consultation_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Consultation type.'
PREFIX_OBJECT = 'cns'
PROPERTIES_OBJECT = {
    'id':                  (0, '', ''),
    'title':               (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':         (0, '', ''),
    'start_date':          (0, MUST_BE_DATETIME, 'The Start Date field must contain a valid date.'),
    'end_date':            (0, MUST_BE_DATETIME, 'The End Date field must contain a valid date.'),
    'sortorder':           (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':         (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'allow_file':          (0, '', ''),
    'line_comments':       (0, '', ''),
    'public_registration': (0, '', ''),
    'lang':                (0, '', '')
}

manage_addNyConsultation_html = PageTemplateFile('zpt/consultation_manage_add', globals())
manage_addNyConsultation_html.kind = METATYPE_OBJECT
manage_addNyConsultation_html.action = 'addNyConsultation'

consultation_add_html = PageTemplateFile('zpt/consultation_add', globals())

def addNyConsultation(self, id='', title='', description='', sortorder='', start_date='', end_date='', public_registration='', 
                            allow_file='',line_comments='', contributor=None, releasedate='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Naaya Consultation type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER

    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'consultation_manage_add' or l_referer.find('consultation_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, sortorder=sortorder, \
            start_date=start_date, end_date=end_date, public_registration=public_registration, line_comments=line_comments)
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
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None) is not None:
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NyConsultation(id, title, description, sortorder, start_date,
                                  end_date, public_registration, allow_file, line_comments, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.submitThis()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'consultation_manage_add' or l_referer.find('consultation_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'consultation_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, \
                sortorder=sortorder, releasedate=releasedate, start_date=start_date, end_date=end_date, 
                allow_file=allow_file, line_comments=line_comments, public_registration=public_registration, lang=lang)
            REQUEST.RESPONSE.redirect('%s/consultation_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

class NyConsultation(NyAttributes, Implicit, NyProperties, BTreeFolder2, NyContainer, NyCheckControl, NyValidation, utils):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    all_meta_types = ()

    icon = 'misc_/NaayaContent/NyConsultation.gif'
    icon_marked = 'misc_/NaayaContent/NyConsultation_marked.gif'

    title = LocalProperty('title')
    description = LocalProperty('description')

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, sortorder, start_date, end_date, public_registration, allow_file, line_comments, contributor, releasedate, lang):
        """ """
        self.id = id
        self.contributor = contributor
        self.questions = {}
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        BTreeFolder2.__init__(self)
        try: del self.title
        except: pass
        self.save_properties(title, description, sortorder, start_date, end_date, public_registration, allow_file, line_comments, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    security.declarePrivate('save_properties')
    def save_properties(self, title, description, sortorder, start_date, end_date, public_registration, allow_file, line_comments, releasedate, lang):
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        
        self.start_date = self.utConvertStringToDateTimeObj(start_date)
        self.end_date = self.utConvertStringToDateTimeObj(end_date)
        self.sortorder = sortorder
        self.releasedate = releasedate
        self.public_registration = public_registration
        self.allow_file = allow_file
        self.line_comments = line_comments

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'saveProperties')
    def saveProperties(self, title='', description='', sortorder='', start_date='', end_date='',
                       public_registration='', allow_file='', line_comments='', file='', lang='', REQUEST=None):
        """ """
        
        if not title:
            self.setSession('title', title)
            self.setSession('description', description)
            self.setSessionErrors(['The Title field must have a value.'])
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        
        if file and not file.read():
            self.setSession('title', title)
            self.setSession('description', description)
            self.setSessionErrors(['File must not be empty'])
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        
        exfile = self.get_exfile()
        
        if file and exfile:
            exfile.saveUpload(file=file, lang=lang)
            downloadfilename=file.filename
            exfile._setLocalPropValue('downloadfilename', lang, downloadfilename)
        elif file and not exfile:
            addNyExFile(self, title=title, file=file, lang=lang, source='file')
            
        releasedate = self.releasedate
        self.save_properties(title, description, sortorder, start_date, end_date, public_registration, allow_file, line_comments, releasedate, lang)
            
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(view, 'get_exfile')
    def get_exfile(self):
        """ Returns the first ExFile in the Consultation, there should be only one. """
        
        try:
            exfile = self.objectValues(['Naaya Extended File'])[0]
        except IndexError:
            exfile = None
            
        return exfile

    security.declareProtected(view, 'check_exfile_for_lang')
    def check_exfile_for_lang(self, lang):
        """ Checks if there is a file uploaded for the given language. """
       
        return self.get_exfile().getFileItem(lang).size > 0

    security.declareProtected(view, 'get_exfile_langs')
    def get_exfile_langs(self):
        """ Returns the languages for witch NyExFile contains files. """
        
        return [language for language in self.getSite().gl_get_languages_map() if self.check_exfile_for_lang(language['id'])]

    security.declareProtected(view, 'get_start_date')
    def get_start_date(self):
        """ Returns the start date in dd/mm/yyyy string format. """
        
        return self.utConvertDateTimeObjToString(self.start_date)

    security.declareProtected(view, 'get_end_date')
    def get_end_date(self):
        """ Returns the end date in dd/mm/yyyy string format. """
        
        return self.utConvertDateTimeObjToString(self.end_date)
    
    security.declareProtected(view, 'get_days_left')
    def get_days_left(self):
        """ Returns the remaining days for the consultation or the number of days before it starts """
        
        today = self.utGetTodayDate().earliestTime()
        
        if self.start_date.lessThanEqualTo(today):
            return (1, int(str(self.end_date - today).split('.')[0]))
        else:
            return (0, int(str(self.start_date - today).split('.')[0]))

    security.declareProtected(view_management_screens, 'manage_options')
    def manage_options(self):
        """ """
        
        l_options = (NyContainer.manage_options[0],)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    security.declareProtected(view, 'check_contributor_comment')
    def check_contributor_comment(self, contributor='', REQUEST=None):
        """ Returns True if user already posted a comment """
        
        if not contributor and REQUEST:
            contributor = REQUEST.AUTHENTICATED_USER.getUserName()
            
        if contributor in [comment.contributor for comment in self.objectValues(['Consultation Comment'])]:
            return True

    security.declareProtected(PERMISSION_REVIEW_CONSULTATION, 'addConsultationReview')
    def addConsultationReview(self, contributor_name, file='', REQUEST=None, **kwargs):
        """ """
        
        contributor = REQUEST.AUTHENTICATED_USER.getUserName()
        if REQUEST:
            kwargs.update(REQUEST.form)
        
        addConsultationReviewItem(self, contributor, contributor_name, file, kwargs)
        
        return REQUEST.RESPONSE.redirect('%s/review_add_html?status=ok' % (self.absolute_url(), ))

    #permissions
    def checkPermissionReviewConsultation(self):
        """
        Check for reviewing the Consultation.
        """
        return self.checkPermission(PERMISSION_REVIEW_CONSULTATION)

    def checkPermissionManageConsultation(self):
        """
        Check for managing the Consultation.
        """
        return self.checkPermission(PERMISSION_MANAGE_CONSULTATION)

    def get_reviews(self):
        """ Returns a list with all the Consultation Review objects """
        return self.objectValues(['Consultation Review'])

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'addQuestion')
    def addQuestion(self, question_body, lang, sortorder, REQUEST=None):
        """ """
        id = 'q%s' % self.utGenRandomId(4)
        
        try: sortorder = int(sortorder)
        except: sortorder = 100
        
        if not self.questions.has_key(id): id = id
        else: id = id + self.utGenRandomId()
        
        self.questions[id] = question_item(question_body, lang, sortorder)
        self._p_changed = 1
        return REQUEST.RESPONSE.redirect('%s/manage_questions_html' % (self.absolute_url(), ))

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'delete_question')
    def delete_question(self, qid, REQUEST=None):
        """ """
        del(self.questions[qid])
        self._p_changed = 1
        return REQUEST.RESPONSE.redirect('%s/manage_questions_html' % (self.absolute_url(), ))

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'edit_question')
    def edit_question(self, qid, question_body, lang, REQUEST=None):
        """ """
        self.questions[qid].save_properties(question_body, lang)
        return REQUEST.RESPONSE.redirect('%s/question_edit_html?qid=%s' % (self.absolute_url(), qid))

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'get_questions')
    def get_questions(self):
        """ Returns the questions sorted by sortorder """
        question_items = self.questions.items()
        question_items.sort(lambda x, y: cmp(x[1].sortorder, y[1].sortorder))
        return question_items

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'getQuestionById')
    def getQuestionById(self, qid):
        """ Returns the question item for the given id"""
        return self.questions[qid]

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'changeSortorder')
    def changeSortorder(self, qid, sortorder):
        """ """
        self.getQuestionById(qid).set_sortorder(sortorder)
        self._p_changed = 1

    def getQuestionBody(self, qid, lang):
        """ Returns the question's body string for the specified language """
        return self.getQuestionById(qid).get_body(lang)

    def getQuestionSortorder(self, qid):
        """ """
        return self.getQuestionById(qid).get_sortorder()

    def review_has_comments(self, review):
        """ """
        return review.linecomments[0]['comment']

    #site pages
    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'question_edit_html')
    question_edit_html = PageTemplateFile('zpt/question_edit', globals())
    
    security.declareProtected(PERMISSION_REVIEW_CONSULTATION, 'review_add_html')
    review_add_html = PageTemplateFile('zpt/review_add', globals())

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'manage_questions_html')
    manage_questions_html = PageTemplateFile('zpt/manage_questions', globals())
    
    security.declareProtected(view, 'index_html')
    reviews_index_html = PageTemplateFile('zpt/reviews_index', globals())
    
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/consultation_index', globals())
    
    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/consultation_edit', globals())
    
InitializeClass(NyConsultation)

