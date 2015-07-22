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
from Products.NaayaContent.constants import *
from Products.Naaya.constants import *
from Products.NaayaBase.constants import *
from Products.Naaya.NyFolder import NyFolder
from Products.NaayaBase.NyCheckControl  import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation

from Products.NaayaContent.NyReportChapter.NyReportChapter import METATYPE_OBJECT as METATYPE_NYREPORTCHAPTER
from Products.NaayaContent.NyReportComment.NyReportComment import METATYPE_OBJECT as METATYPE_NYREPORTCOMMENT
from Products.NaayaContent.NyReportReference.NyReportReference import METATYPE_OBJECT as METATYPE_NYREPORTREFERENCE
import babelizer

#module constants
METATYPE_OBJECT = 'Naaya Report'
LABEL_OBJECT = 'Report'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Report objects'
OBJECT_FORMS = ['report_add', 'report_edit', 'report_index', 'report_macro_objecttree', 'report_macro_sec_objecttree', 'report_references', 'report_comments']
OBJECT_CONSTRUCTORS = ['manage_addNyReport_html', 'report_add_html', 'addNyReport', 'importNyReport']
OBJECT_ADD_FORM = 'report_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Report type.'
PREFIX_OBJECT = 'rep'
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
        'module': 'NyReport',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Report',
        'label': 'Report',
        'permission': 'Naaya - Add Naaya Report objects',
        'forms': ['report_add', 'report_edit', 'report_index'],
        'add_form': 'report_add_html',
        'description': 'This is Naaya Report type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': None,
        'schema_name': '',
        'import_string': 'importNyReport',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyReport.gif'),
        '_misc': {
                'NyReport.gif': ImageFile('www/NyReport.gif', globals()),
                'NyReport_marked.gif': ImageFile('www/NyReport_marked.gif', globals()),
            },
    }

def report_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyReport'}, 'report_add')

def addNyReport(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Report type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'report_manage_add' or l_referer.find('report_manage_add') != -1) and REQUEST:
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
        folder_meta_types = ['Naaya Report Chapter', 'Naaya File', 'Naaya Section Comment']
        #create object
        ob = NyReport(id, title, description, coverage, keywords, sortorder, contributor, releasedate, folder_meta_types, lang)
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
            if l_referer == 'report_manage_add' or l_referer.find('report_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'report_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, lang=lang)
            REQUEST.RESPONSE.redirect('%s/report_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNyReport(self, param, id, attrs, content, properties, discussion, objects):
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
#            addNyReport(self, id=id,
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

class NyReport(NyFolder, NyCheckControl):
    """ """
    
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyReport.gif'
    icon_marked = 'misc_/NaayaContent/NyReport_marked.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, contributor, releasedate, folder_meta_types, lang):
        """ """
        NyFolder.__dict__['__init__'](self, id, title, description, coverage, keywords, sortorder, 0, '', contributor, folder_meta_types, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)

    #Related API
    def getReport(self):
        return self

    def getChapters(self):
        return self.utSortObjsListByAttr(self.objectValues(METATYPE_NYREPORTCHAPTER),'sortorder',0)

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteComments')
    def deleteComments(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/reportcomments_html' % self.absolute_url())

    def getCrossReferences(self):
        return self.objectValues(METATYPE_NYREPORTREFERENCE)

    def getAllComments(self):
        return self.objectValues(METATYPE_NYREPORTCOMMENT)

    def hasComments(self):
        return len(self.objectValues(METATYPE_NYREPORTCOMMENT))

    def translate_comment(self, phrase, from_lang='', to_lang='', REQUEST=None):
        """ """
        if not phrase.strip():  return ''
        try:                    return babelizer.translate(phrase, from_lang, to_lang)
        except:                 return ''

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/report_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_edit')

    security.declareProtected(view, 'reportreferences_html')
    def reportreferences_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_references')

    security.declareProtected(view, 'reportcomments_html')
    def reportcomments_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_comments')

    security.declareProtected(view, 'report_macro_objecttree_html')
    def report_macro_objecttree_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getForm('report_macro_objecttree')

    security.declareProtected(view, 'report_macro_sec_objecttree_html')
    def report_macro_sec_objecttree_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getForm('report_macro_sec_objecttree')

    #path for AuthenticationTool
    def getUserEmail(self, user_str):
        """ """
        auth_tool = self.getAuthenticationTool()
        user_obj = auth_tool.getUser(user_str)
        if user_obj is not None:
            return user_obj.email
        return ''

InitializeClass(NyReport)
manage_addNyReport_html = PageTemplateFile('zpt/report_manage_add', globals())
manage_addNyReport_html.kind = METATYPE_OBJECT
manage_addNyReport_html.action = 'addNyReport'

config.update({
    'constructors': (manage_addNyReport_html, addNyReport),
    'folder_constructors': [
            # NyFolder.manage_addNyReport_html = manage_addNyReport_html
            ('manage_addNyReport_html', manage_addNyReport_html),
            ('report_add_html', report_add_html),
            ('addNyReport', addNyReport),
            (config['import_string'], importNyReport),
        ],
    'add_method': addNyReport,
    'validation': issubclass(NyReport, NyValidation),
    '_class': NyReport,
})

def get_config():
    return config
