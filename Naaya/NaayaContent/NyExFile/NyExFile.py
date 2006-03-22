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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Zope imports
from OFS.Image import File, cookId
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from exfile_item import exfile_item

#module constants
METATYPE_OBJECT = 'Naaya Extended File'
LABEL_OBJECT = 'File'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Extended File objects'
OBJECT_FORMS = ['exfile_add', 'exfile_edit', 'exfile_index']
OBJECT_CONSTRUCTORS = ['manage_addNyExFile_html', 'exfile_add_html', 'addNyExFile', 'importNyExFile']
OBJECT_ADD_FORM = 'exfile_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Extended File type.'
PREFIX_OBJECT = 'exfile'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'file':             (0, '', ''),
    'url':              (0, '', ''),
    'downloadfilename': (0, '', ''),
    'content_type':     (0, '', ''),
    'lang':             (0, '', '')
}

manage_addNyExFile_html = PageTemplateFile('zpt/exfile_manage_add', globals())
manage_addNyExFile_html.kind = METATYPE_OBJECT
manage_addNyExFile_html.action = 'addNyExFile'

def exfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyExFile'}, 'exfile_add')

def addNyExFile(self, id='', title='', description='', coverage='', keywords='', sortorder='',
    source='file', file='', url='', precondition='', content_type='', downloadfilename='',
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a File type of object.
    """
    if source=='file': id = cookId(id, title, file)[0] #upload from a file
    id = self.utCleanupId(id)
    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    if downloadfilename == '': downloadfilename = id
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'exfile_manage_add' or l_referer.find('exfile_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, file=file, url=url, \
            downloadfilename=downloadfilename)
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
        ob = NyExFile(id, title, description, coverage, keywords, sortorder, '', precondition, content_type,
            downloadfilename, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.submitThis()
        ob.approveThis(approved, approved_by)
        ob.handleUpload(source, file, url, lang)
        ob.file_for_lang(lang).createVersion(self.REQUEST)
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'file_manage_add' or l_referer.find('file_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'file_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                url=url, downloadfilename=downloadfilename, lang=lang)
            REQUEST.RESPONSE.redirect('%s/file_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)


def importNyExFile(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    pass

class NyExFile(NyAttributes, exfile_item, NyItem, NyCheckControl, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyExFile.gif'
    icon_marked = 'misc_/NaayaContent/NyExFile_marked.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, file, precondition,
        content_type, downloadfilename, contributor, releasedate, lang):
        """ """
        self.id = id
        exfile_item.__dict__['__init__'](self, id, title, description, coverage, keywords, sortorder, file,
            precondition, content_type, downloadfilename, releasedate, lang)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += exfile_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    #override handlers
    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        NyExFile.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        NyExFile.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

    security.declarePublic('showVersionData')
    def showVersionData(self, vid=None, REQUEST=None, RESPONSE=None):
        """ """
        if vid:
            lang = self.gl_get_selected_language()
            cur_file = self.file_for_lang(lang)
            version_data = self.getVersion(vid)
            if version_data is not None:
                #show data for file: set content type and return data
                RESPONSE.setHeader('Content-Type', version_data[1])
                REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename)
                return version_data[0]
            else:
                return 'Invalid version data!'
        else:
            return 'Invalid version id!'

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/exfile_manage_edit', globals())

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'exfile_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'exfile_edit')

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename)
        return file_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        return file_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

InitializeClass(NyExFile)