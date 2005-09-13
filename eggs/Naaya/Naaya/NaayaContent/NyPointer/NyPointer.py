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

#Python imports
from copy import deepcopy

#Zope imports
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
from pointer_item import pointer_item

#module constants
METATYPE_OBJECT = 'Naaya Pointer'
LABEL_OBJECT = 'Pointer'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Pointer objects'
OBJECT_FORMS = ['pointer_add', 'pointer_edit', 'pointer_index']
OBJECT_CONSTRUCTORS = ['manage_addNyPointer_html', 'pointer_add_html', 'addNyPointer', 'importNyPointer']
OBJECT_ADD_FORM = 'pointer_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Pointer type.'
PREFIX_OBJECT = 'pnt'

manage_addNyPointer_html = PageTemplateFile('zpt/pointer_manage_add', globals())
manage_addNyPointer_html.kind = METATYPE_OBJECT
manage_addNyPointer_html.action = 'addNyPointer'

def pointer_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyPointer'}, 'pointer_add')

def addNyPointer(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', pointer='', contributor=None, releasedate='', discussion='',
    lang=None, REQUEST=None, **kwargs):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.checkPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.utConvertStringToDateTimeObj(releasedate)
    if releasedate is None: releasedate = self.utGetTodayDate()
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyPointer(id, title, description, coverage, keywords, sortorder, pointer,
        contributor, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
    self._setObject(id, ob)
    if discussion: self._getOb(id).open_for_comments()
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'pointer_manage_add' or l_referer.find('pointer_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'pointer_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/note_html' % self.getSitePath())

def importNyPointer(self, id, attrs, content, properties):
    #this method is called during the import process
    addNyPointer(self, id=id,
        sortorder=attrs['sortorder'].encode('utf-8'),
        pointer=attrs['pointer'].encode('utf-8'),
        contributor=attrs['contributor'].encode('utf-8'))
    ob = self._getOb(id)
    for property, langs in properties.items():
        for lang in langs:
            ob._setLocalPropValue(property, lang, langs[lang])
    ob.approveThis(abs(int(attrs['approved'].encode('utf-8'))))
    ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
    ob.checkThis(attrs['validation_status'].encode('utf-8'),
        attrs['validation_comment'].encode('utf-8'),
        attrs['validation_by'].encode('utf-8'),
        attrs['validation_date'].encode('utf-8'))
    self.recatalogNyObject(ob)

class NyPointer(NyAttributes, pointer_item, NyItem, NyCheckControl, NyValidation):
    """ """

    meta_type = METATYPE_OBJECT
    icon = 'misc_/NaayaContent/NyPointer.gif'
    icon_marked = 'misc_/NaayaContent/NyPointer_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += pointer_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, pointer,
        contributor, approved, approved_by, releasedate, lang):
        """ """
        self.id = id
        pointer_item.__dict__['__init__'](self, title, description, coverage, keywords, sortorder, pointer, releasedate, lang)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self.approved = approved
        self.approved_by = approved_by

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'pointer="%s" validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
            (self.utXmlEncode(self.pointer),
                self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language='', coverage='',
        keywords='', sortorder='', approved='', pointer='', releasedate='',
        discussion='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.releasedate
        lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, pointer, releasedate, lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
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
        self.sortorder = self.version.sortorder
        self.pointer = self.version.pointer
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
        if self.version.is_open_for_comments(): self.open_for_comments()
        else: self.close_for_comments()
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
        #check permissions
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = pointer_item(self.title, self.description, self.coverage, self.keywords, self.sortorder,
            self.pointer, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        if self.is_open_for_comments(): self.version.open_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', pointer='', releasedate='', discussion='', lang=None,
        REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.releasedate
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            self.save_properties(title, description, coverage, keywords, sortorder, pointer, releasedate, lang)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.save_properties(title, description, coverage, keywords, sortorder, pointer, releasedate, lang)
            self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.version.open_for_comments()
            else: self.version.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/pointer_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'pointer_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'pointer_edit')

InitializeClass(NyPointer)
