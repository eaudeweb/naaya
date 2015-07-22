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
import os
import sys
from copy import deepcopy

#Zope imports
from Globals                                    import InitializeClass
from App.ImageFile import ImageFile
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
import Products

#Product imports
from Products.NaayaContent.constants    import *
from Products.NaayaBase.constants       import *
from Products.Naaya.NyFolder import NyFolder
from Products.NaayaBase.NyCheckControl  import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation

from Products.NaayaContent.NyReportSection.NyReportSection import METATYPE_OBJECT as METATYPE_NYREPORTSECTION
from Products.NaayaContent.NyReportQuestion.NyReportQuestion import METATYPE_OBJECT as METATYPE_NYREPORTQUESTION
from Products.NaayaContent.NyReportQuestionnaire.NyReportQuestionnaire import METATYPE_OBJECT as METATYPE_NYREPORTQUESTIONNAIRE
from Products.NaayaContent.NySectionComment.NySectionComment import METATYPE_OBJECT as METATYPE_NYSECTIONCOMMENT

#CHM custom constants
PDF_FILENAME = 'chapter_en.pdf'

#module constants
PERMISSION_ADD_ANSWER = 'Naaya - Add Naaya Report Chapter objects'
METATYPE_OBJECT = 'Naaya Report Chapter'
LABEL_OBJECT = 'Report Chapter'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Report Chapter objects'
OBJECT_FORMS = ['reportchapter_add', 'reportchapter_edit', 'reportchapter_index', 'chapter_comments']
OBJECT_CONSTRUCTORS = ['manage_addNyReportChapter_html', 'reportchapter_add_html', 'addNyReportChapter', 'importNyReportChapter']
OBJECT_ADD_FORM = 'reportchapter_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Report Chapter type.'
PREFIX_OBJECT = 'chp'
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

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'NyReportChapter',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Report Chapter',
        'label': 'Report Chapter',
        'permission': 'Naaya - Add Naaya Report Chapter objects',
        'forms': ['reportchapter_add', 'reportchapter_edit', 'reportchapter_index'],
        'add_form': 'reportchapter_add_html',
        'description': 'This is Naaya Report Chapter type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': None,
        'schema_name': '',
        'import_string': 'importNyReportChapter',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyReportChapter.gif'),
        '_misc': {
                'NyReportChapter.gif': ImageFile('www/NyReportChapter.gif', globals()),
                'NyReportChapter_marked.gif': ImageFile('www/NyReportChapter_marked.gif', globals()),
            },
    }

def reportchapter_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyReportChapter'}, 'reportchapter_add')

def addNyReportChapter(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Report Chapter type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'manage_addNyReportChapter_html' or l_referer.find('manage_addNyReportChapter_html') != -1) and REQUEST:
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
        if self.meta_type == self.getSite().meta_type: 
            folder_meta_types = self.getSite().adt_meta_types
        else:
            folder_meta_types = self.folder_meta_types
        folder_meta_types = ['Naaya Report Chapter', 'Naaya File', 'Naaya Section Comment', 'Naaya Report Section']
        #create object
        ob = NyReportChapter(id, title, description, coverage, keywords, sortorder, contributor, releasedate, folder_meta_types, lang)
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
            if l_referer == 'manage_addNyReportChapter_html' or l_referer.find('manage_addNyReportChapter_html') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'reportchapter_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, lang=lang)
            REQUEST.RESPONSE.redirect('%s/reportchapter_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNyReportChapter(self, param, id, attrs, content, properties, discussion, objects):
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
#            addNyReportChapter(self, id=id,
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

class NyReportChapter(NyFolder, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyReportChapter.gif'
    icon_marked = 'misc_/NaayaContent/NyReportChapter_marked.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, contributor, releasedate, folder_meta_types, lang):
        """ """
        NyFolder.__dict__['__init__'](self, id, title, description, coverage, keywords, sortorder, 0, '', contributor, folder_meta_types, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteComments')
    def deleteComments(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/chaptercomments_html' % self.absolute_url())

    def getAllComments(self):
        return self.objectValues(METATYPE_NYSECTIONCOMMENT)

    def hasComments(self):
        return len(self.objectValues(METATYPE_NYSECTIONCOMMENT))

    def getChapter(self): return self
    def getChapterPath(self): return self.absolute_url()

    def getSections(self): return self.utSortObjsListByAttr(self.objectValues(METATYPE_NYREPORTSECTION),'sortorder',0)
    def getQuestions(self): return self.utSortObjsListByAttr(self.objectValues(METATYPE_NYREPORTQUESTION),'sortorder',0)
    def hasQuestions(self):
        return len(self.getQuestions()) > 0

    #CHM custom
#    def getQuestionsLocation(self):
#        if self.hasQuestions(): return self
#        else:                   return None

    def getQuestionnaires(self): return self.utSortObjsListByAttr(self.objectValues(METATYPE_NYREPORTQUESTIONNAIRE),'sortorder',0)
    def hasQuestionnaires(self):
        return len(self.getQuestionnaires()) > 0

    def getRateValue(self, qnr, rate):
        """ """
        try:
            return qnr.ratings[rate.title]
        except:
            return None

    def getQuestionIds(self):
        obs = self.objectValues(METATYPE_NYREPORTQUESTION)
        obs = self.utSortObjsListByAttr(obs,'sortorder',0)
        return [ob.id for ob in obs]
    def getQuestionById(self,p_id):
        return self._getOb(p_id)

    def getNavigationInfo(self):
        l_up = self.getParentNode()
        siblings = l_up.getChapters()
        l_prev = None
        l_next = None
        l_temp = None
        for obj in siblings:
            if(obj==self): l_prev = l_temp
            if(l_temp==self): l_next = obj
            l_temp = obj;
        return [l_prev, l_up, l_next]

    security.declareProtected(view, 'toc')
    def toc(self):
        """ return the table of contents """
        return self.getParentNode().absolute_url()

    def checkPermissionAddAnswers(self, context):
        """
        Check for adding answers permission in the given context.
        """
        return context.checkPermission(PERMISSION_ADD_ANSWER)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/reportchapter_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportchapter_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportchapter_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'reportchapter_edit')

    security.declareProtected(view, 'report_macro_objecttree_html')
    def report_macro_objecttree_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getForm('report_macro_objecttree')

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

    def getQuestionsLocation(self):
        if hasattr(self, PDF_FILENAME): return self
        else:                           return None

    security.declareProtected(view, 'chaptercomments_html')
    def chaptercomments_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'chapter_comments')

InitializeClass(NyReportChapter)

manage_addNyReportChapter_html = PageTemplateFile('zpt/reportchapter_manage_add', globals())
manage_addNyReportChapter_html.kind = METATYPE_OBJECT
manage_addNyReportChapter_html.action = 'addNyReportChapter'

config.update({
    'constructors': (manage_addNyReportChapter_html, addNyReportChapter),
    'folder_constructors': [
            # NyFolder.manage_addNyReportChapter_html = manage_addNyReportChapter_html
            ('manage_addNyReportChapter_html', manage_addNyReportChapter_html),
            ('reportchapter_add_html', reportchapter_add_html),
            ('addNyReportChapter', addNyReportChapter),
            (config['import_string'], importNyReportChapter),
        ],
    'add_method': addNyReportChapter,
    'validation': issubclass(NyReportChapter, NyValidation),
    '_class': NyReportChapter,
})

def get_config():
    return config



