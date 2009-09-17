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
# Alex Morega, Eau de Web

#Python imports
import os
import sys
from datetime import datetime
import urllib

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Image import cookId
from persistent.list import PersistentList

#Product imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaBase.NyContentType import (
    NyContentData, NyContentType, NY_CONTENT_BASE_SCHEMA)
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyFolderishVersioning import NyFolderishVersioning

from NyBlobFile import NyBlobFile

#module constants
DEFAULT_SCHEMA = {
    # add NyBFile-specific properties here
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'bfile_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Blob File',
        'label': 'BFile',
        'permission': 'Naaya - Add Naaya Blob File objects',
        'forms': ['bfile_add', 'bfile_edit', 'bfile_index'],
        'add_form': 'bfile_add_html',
        'description': 'File objects that store data using ZODB BLOBs',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyBFile',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'bfile.gif'),
        '_misc': {
                'NyBFile.gif': ImageFile('www/bfile.gif', globals()),
                'NyBFile_marked.gif': ImageFile('www/bfile_marked.gif', globals()),
            },
    }

def bfile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyBFile', 'form_helper': form_helper}, 'bfile_add')

def _create_NyBFile_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyBFile(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyBFile(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a BFile type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    _uploaded_file = schema_raw_data.pop('uploaded_file', None)
    _contact_word = schema_raw_data.get('contact_word', '')

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = 'doc' + self.utGenRandomId(5)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyBFile_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/bfile_add_html' % self.absolute_url())
            return

    if _uploaded_file is not None:
        ob._save_file(_uploaded_file)

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'bfile_manage_add' or l_referer.find('bfile_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'bfile_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

class NyBFile(NyContentData, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyBFile.gif'
    icon_marked = 'misc_/NaayaContent/NyBFile_marked.gif'

    manage_options = (
        {'label': 'Properties', 'action': 'manage_edit_html'},
        {'label': 'Edit', 'action': 'manage_main'},
        {'label': 'View', 'action': 'index_html'},
    ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyContentData.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self._versions = PersistentList()

    #XXX Should remove NyCheckControl inheritance and refactor code to not use
    # NyCheckControl methods.
    def isVersionable(self):
        """ BFile objects are not versionable """
        return False

    security.declarePrivate('current_version')
    @property
    def current_version(self):
        for ver in reversed(self._versions):
            if not getattr(ver, 'removed', False):
                return ver
        else:
            return None

    def _save_file(self, the_file):
        meta = {
            'filename': the_file.filename,
            'content_type': 'application/octet-stream',
            'timestamp': datetime.utcnow(),
        }
        bf = NyBlobFile(**meta)

        # copy file data
        bf_stream = bf.open_write()
        bf_stream.write(the_file.read()) # TODO: copy data in chunks
        bf_stream.close()

        self._versions.append(bf)

    security.declarePrivate('remove_version')
    def remove_version(self, number):
        ver = self._versions[number]
        ver.removed = True
        ver.removed_at = datetime.utcnow()
        ver.removed_by = None # TODO
        f = ver.open_write()
        f.write('')
        f.close()

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _uploaded_file = schema_raw_data.pop('uploaded_file', None)

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)

        if _uploaded_file is not None:
            self._save_file(_uploaded_file)

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'bfile_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'bfile_edit')

    # TODO: security
    def download(self, REQUEST, RESPONSE):
        """ serve the current_version file """
        ver = self.current_version
        if ver is None:
            raise NotImplementedError # TODO

        RESPONSE.setHeader('Content-Type', ver.content_type)
        #RESPONSE.setHeader('Content-Length', ver.size) # TODO
        RESPONSE.setHeader('Content-Disposition',
            "attachment;filename*=UTF-8''%s" % urllib.quote(ver.filename))

        # TODO: stream the response
        f = ver.open()
        data = f.read()
        f.close()
        return data

InitializeClass(NyBFile)

config.update({
    'constructors': (addNyBFile,),
    'folder_constructors': [
            ('bfile_add_html', bfile_add_html),
            ('addNyBFile', addNyBFile),
        ],
    'add_method': addNyBFile,
    'validation': issubclass(NyBFile, NyValidation),
    '_class': NyBFile,
})

def get_config():
    return config
