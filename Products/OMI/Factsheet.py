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
# Alex Morega, Eau de Web
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from OFS.Folder import Folder
from Globals import InitializeClass
import Acquisition
from AccessControl import ClassSecurityInfo
from datetime import datetime
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.CatalogAwareness import CatalogAware

import re

import scrubber
if 'any' not in dir(__builtins__):
    from Products.NaayaCore.backport import any
    scrubber.any = any
sanitize = scrubber.Scrubber().scrub


def trim(message):
    """ Remove leading and trailing empty paragraphs """
    message = re.sub(r'^\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*', '', message)
    message = re.sub(r'\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*$', '', message)
    return message


def cleanup_message(message):
    return sanitize(trim(message)).strip()

from constants import *
from utilities import *

from FactsheetComment import manage_addComment


def get_parent(value):
    for pair in analytical_techniques:
        for element in pair[1]:
            if element == value:
                return pair[0]


class Dummy(Acquisition.Implicit, object):
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self):
        self.id = ''

    def get_parent_of(self, value):
        # The function returns the cathegory of an already selected item,
        # so we know where to return it (when removed)
        return get_parent(value)

    def is_entitled(self, REQUEST):
        return False

InitializeClass(Dummy)

dummy = Dummy()
for name in form_names:
    setattr(dummy, name, "")
for list in form_lists:
    setattr(dummy, list, [])

_manage_addFactsheet_html = PageTemplateFile('zpt/factsheet', globals())


def manage_addFactsheet_html(self, REQUEST):
    """ Method for adding a Factsheet object """

    # first time in page the context is a dummy object
    context = dummy.__of__(self)
    submit = REQUEST.get('submit', '')

    if submit:

        # during the add process the object will be stored in a teporary folder
        id = REQUEST.form.get('object_id', '')
        root = self.unrestrictedTraverse('/')
        temp_folder = root.temp_folder
        temp_object = temp_folder._getOb(id, None)

        # get the current page
        page = int(REQUEST.form.get('page', 1))
        if page == 1:
            if form_validation(mandatory_fields_model, REQUEST,
                               **REQUEST.form):
                if temp_object is None:
                    id = slugify(REQUEST.form.get('title', ''))
                    if not id:
                        id = generate_id()
                    id = get_available_id(self, temp_folder, id)
                    newFactsheet = Factsheet(id)
                    temp_folder._setObject(id, newFactsheet)
                    temp_object = temp_folder._getOb(id)
                temp_object.edit(REQUEST.form)
                context = temp_object
                REQUEST.set('page', 2)
            else:
                REQUEST.set('page', 1)

        elif page == 2:
            temp_object.edit(REQUEST.form)
            context = temp_object
            if submit == 'Next':
                REQUEST.set('page', 3)
            elif submit == 'Upload picture':
                REQUEST.set('page', 2)
            else:
                REQUEST.set('page', 1)

        elif page == 3:
            temp_object.edit(REQUEST.form)
            context = temp_object
            if submit == 'Next':
                REQUEST.set('page', 4)
            else:
                REQUEST.set('page', 2)

        elif page == 4:
            if submit == 'Previous':
                temp_object.edit(REQUEST.form)
                context = temp_object
                REQUEST.set('page', 3)
            else:
                # generate an access password, set creation date
                # and finally move the object back to the original folder
                password = self.generate_password(temp_object.contact_email)
                temp_object.password = password
                temp_object.created = datetime.now()
                temp_object.last_modified = ''
                # set credentials so that the person who adds a model
                # can also edit it during the session's validity
                REQUEST.SESSION.set('authentication_email',
                                    temp_object.contact_email)
                REQUEST.SESSION.set('authentication_password', password)
                # Move the object in the Factsheet Folder
                clipboard = temp_folder.manage_copyObjects((id))
                self.manage_pasteObjects(clipboard)
                # catalog the final object
                factsheet_object = self._getOb(id)
                factsheet_object.reindex_object()
                temp_folder.manage_delObjects((id))
                # @todo to study how can we use cut/paste
                # (now: permission denied)
                factsheet_object.assign_password_notification(
                    factsheet_object.contact_email, password)
                factsheet_object.model_add_edit_notification(
                    self.administrator_email)
                self.add_message('Model successfully added!')
                REQUEST.RESPONSE.redirect(factsheet_object.absolute_url())
                return

    return _manage_addFactsheet_html.__of__(self)(
        REQUEST, potential_themes=potential_themes,
        potential_coverage=potential_coverage,
        potential_resolution=potential_resolution,
        potential_time_horizon=potential_time_horizon,
        potential_time_steps=potential_time_steps,
        accessibility_levels=accessibility_levels,
        analytical_techniques=analytical_techniques, context=context)

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$',
                        re.IGNORECASE)


def form_validation(mandatory_fields, REQUEST, **kwargs):
    has_errors = False
    for k, v in kwargs.items():
        if k in mandatory_fields:
            if (k == 'contact_email' or k == 'authentication_email') and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_notvalid' % k, True)
                    has_errors = True
            if not v:
                REQUEST.set('%s_error' % k, True)
                has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)

    return not has_errors


class Factsheet(CatalogAware, Folder):

    default_catalog = 'catalogue'
    meta_type = "OMI Factsheet"
    security = ClassSecurityInfo()

    def __init__(self, id):
        """ constructor """
        super(Factsheet, self).__init__(id)
        self.id = id
        for name in form_names:
            setattr(self, name, u'')
        for list in form_lists:
            setattr(self, list, [])

    security.declarePrivate('edit')

    def edit(self, data):
        # @todo: eliminate form lists hardcodings (contained in page2)
        page = int(data.get('page', 1))
        # we assume that all selection lists are in page 2.
        # the next block handles the case when the user sends an empty
        # lists and 'we' receive nothing.
        if page == 2:
            for key in form_lists:
                data.setdefault(key, [])
        for key in data.keys():
            if key in form_names:
                if key in form_text_areas:
                    setattr(self, key, cleanup_message(data.get(key, u'')))
                else:
                    setattr(self, key, data.get(key, u''))
            if key in form_lists:
                setattr(self, key, filter(None, data.get(key, [])))
            if key == 'structure_file' and data[key]:
                # @todo: poate fi scrisa mai elegant cu isinstance or something
                self.manage_addFile(id=slugify(data[key].filename),
                                    file=data[key])

    manage_addComment = manage_addComment

    security.declareProtected('Naaya - Add comments for content',
                              'add_comment_html')

    def add_comment_html(self):
        """ """
        return self.manage_addComment(self.REQUEST)

    security.declareProtected(view, 'model_keywords')

    def model_keywords(self):
        """ concatenate all searchable fields in one field """
        keywords = []
        for field in searchable_fields:
            keywords.append(getattr(self, field, ''))
        return u' '.join(keywords)

    security.declareProtected(view, 'getPictures')

    def getPictures(self):
        """ return the available emodel pictures """
        return self.objectValues('File')

    security.declareProtected(view, 'getComments')

    def getComments(self, parent_name):
        """ return the available comments"""
        output = []
        for element in self.objectValues('OMI Factsheet Comment'):
            if element.parent_name == parent_name:
                output.append(element)
        return sortObjsList(output, 'created', False)

    security.declareProtected(MANAGE_FACTSHEET, 'removePicture')

    def removePicture(self, pic_id, REQUEST):
        """ Remove a picture"""
        self.manage_delObjects((pic_id))
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(MANAGE_FACTSHEET, 'deleteObject')

    def deleteObject(self, REQUEST):
        """ Remove an object"""
        id = REQUEST.form.get('object_id')
        self.manage_delObjects(id)
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    _index_html = PageTemplateFile('zpt/factsheet_view', globals())

    security.declareProtected(view, 'index_html')

    def index_html(self, REQUEST):
        """ default view """
        from FactsheetComment import manage_addComment
        if 'add_comment' in REQUEST.form:
            form_valid = form_validation(mandatory_fields_comment, REQUEST,
                                         **REQUEST.form)
            captcha_error = self.captcha_error(REQUEST)
            if form_valid and not captcha_error:
                manage_addComment(self, REQUEST.get('parent_name'),
                                  REQUEST.form)
                return REQUEST.RESPONSE.redirect('%s?page=4' %
                                                 self.absolute_url())
            REQUEST.set('comment', REQUEST.get('comment'))
            REQUEST.set('captcha_error', True)
        return self._index_html(REQUEST)

    security.declareProtected('Naaya - Add comments for content',
                              'comment_form')
    comment_form = PageTemplateFile('zpt/comment', globals())
    security.declarePublic('comment_view')
    comment_view = PageTemplateFile('zpt/comment_view', globals())
    _edit_html = PageTemplateFile('zpt/factsheet', globals())

    security.declareProtected(MANAGE_FACTSHEET, 'edit_html')

    def edit_html(self, REQUEST):
        """ Method for editing existing Factsheets - existing object """
        context = self
        session = REQUEST.SESSION
        submit = REQUEST.form.get('submit', '')
        if 'authenticate' in REQUEST.form:
            REQUEST.set('authentication_try', False)
            # if the user has submitted a valid email and a password,
            # these are saved on the session
            if form_validation(mandatory_fields_authentication, REQUEST,
                               **REQUEST.form):
                session.set('authentication_email',
                            REQUEST.get('authentication_email'))
                session.set('authentication_password',
                            REQUEST.get('authentication_password'))
                REQUEST.set('authentication_try', True)
            REQUEST.set('authentication_password', '')
        if 'retrieve_password' in REQUEST.form:
            email = REQUEST.form.get('email', '')
            if self.contact_email == email:
                self.assign_password_notification(self.contact_email,
                                                  self.password)
                REQUEST.set('password_resent', True)
                self.add_message('Email successfully sent.')
            else:
                REQUEST.set('wrong_email', True)
        if submit:
            # for the editing process we create a copy of the object in
            # the temporary folder and do all the editing there
            # id=self.id
            id = REQUEST.form.get('object_id', '')
            folder = self.getParentNode()
            root = self.unrestrictedTraverse('/')
            temp_folder = root.temp_folder
            temp_object = temp_folder._getOb(id, None)

            # get the current page
            page = int(REQUEST.form.get('page', 1))
            if page == 1:
                if form_validation(mandatory_fields_model, REQUEST,
                                   **REQUEST.form):
                    if temp_object is None:
                        clipboard = self.getParentNode().manage_copyObjects(id)
                        temp_folder.manage_pasteObjects(clipboard)
                        temp_object = temp_folder._getOb(id)
                        temp_object.manage_delObjects(temp_object.objectIds(
                            ['OMI Factsheet Comment']))

                    temp_object.edit(REQUEST.form)
                    context = temp_object
                    REQUEST.set('page', 2)
                else:
                    REQUEST.set('page', 1)

            elif page == 2:
                temp_object.edit(REQUEST.form)
                context = temp_object
                if submit == 'Next':
                    REQUEST.set('page', 3)
                elif submit == 'Upload picture':
                    REQUEST.set('page', 2)
                else:
                    REQUEST.set('page', 1)

            elif page == 3:
                temp_object.edit(REQUEST.form)
                context = temp_object
                if submit == 'Next':
                    REQUEST.set('page', 4)
                else:
                    REQUEST.set('page', 2)

            elif page == 4:
                temp_object.edit(REQUEST.form)
                context = temp_object
                if submit == 'Previous':
                    REQUEST.set('page', 3)
                else:
                    # set modification date, get comments from the old
                    # version of the model and then replace it
                    temp_object.last_modified = datetime.now()
                    factsheet_object = folder._getOb(id)
                    clipboard = factsheet_object.manage_copyObjects(
                        factsheet_object.objectIds(['OMI Factsheet Comment']))
                    temp_object.manage_pasteObjects(clipboard)
                    clipboard = temp_folder.manage_copyObjects(id)
                    folder.manage_delObjects(id)
                    folder.manage_pasteObjects(clipboard)
                    # catalog the final object
                    factsheet_object = folder._getOb(id)
                    factsheet_object.reindex_object()
                    temp_folder.manage_delObjects(id)
                    # @todo to study how can we use cut/paste
                    # (now: permission denied)
                    factsheet_object.model_add_edit_notification(
                        self.administrator_email)
                    self.add_message('Model successfully saved!')
                    REQUEST.RESPONSE.redirect(self.absolute_url())
                    return

        return self._edit_html(REQUEST, potential_themes=potential_themes,
                               potential_coverage=potential_coverage,
                               potential_resolution=potential_resolution,
                               potential_time_horizon=potential_time_horizon,
                               potential_time_steps=potential_time_steps,
                               accessibility_levels=accessibility_levels,
                               analytical_techniques=analytical_techniques,
                               context=context)

    # The function returns the cathegory of an already selected item,
    # so we know where to return it (when removed)
    def get_parent_of(self, value):
        return get_parent(value)

    # notifications
    security.declarePrivate('assign_password_notification')

    def assign_password_notification(self, email, password):
        """ send an email with the password"""
#        mailhost = self.get_mailhost()
#        if mailhost:
        values = {'password': password,
                  'administrator_email': email,
                  'model_view_link': '%s' % self.absolute_url(),
                  'model_edit_link': '%s/edit_html' % self.absolute_url()
                  }
        self.send_mail(msg_to=email,
                       msg_subject='%s - Model access' % self.title,
                       msg_body=ASSIGN_PASSWORD_TEMPLATE % values,
                       msg_body_text=ASSIGN_PASSWORD_TEMPLATE_TEXT % values
                       )

    security.declarePrivate('model_add_edit_notification')

    def model_add_edit_notification(self, email):
        """ send a notification when a folder is added / edited / commented"""
#        mailhost = self.get_mailhost()
#        if mailhost:
        values = {'model_view_link': '%s' % self.absolute_url()}
        self.send_mail(msg_to=email,
                       msg_subject='%s - Model added / edited' % self.title,
                       msg_body=MODEL_ADD_EDIT_TEMPLATE % values,
                       msg_body_text=MODEL_ADD_EDIT_TEMPLATE_TEXT % values
                       )

    security.declarePrivate('model_add_comment_notification')

    def model_add_comment_notification(self, email, page, comment_id,
                                       comment_author):
        """ send a notification when a comment is added to a model """
#        mailhost = self.get_mailhost()
#        if mailhost:
        values = {'model_view_link': '%s?page=%s#Comment-%s' %
                  (self.absolute_url(), page, comment_id),
                  'comment_author': comment_author
                  }
        self.send_mail(msg_to=email,
                       msg_subject='A comment was added for the model %s'
                       % self.title,
                       msg_body=MODEL_ADD_COMMENT_TEMPLATE % values,
                       msg_body_text=MODEL_ADD_COMMENT_TEMPLATE_TEXT % values
                       )

    def is_entitled(self, REQUEST):
        session = REQUEST.SESSION
        return (session.get('authentication_email', '') == (
            self.contact_email and
            session.get('authentication_password', '') == self.password) or
            self.canManageFactsheet())

    security.declarePublic('canManageFactsheet')

    def canManageFactsheet(self):
        """ Check the permissions to edit/delete factsheets """
        return checkPermission(MANAGE_FACTSHEET, self)

    def captcha_error(self, REQUEST):
        if not self.checkPermissionSkipCaptcha():
            recaptcha_response = REQUEST.get('g-recaptcha-response', '')
            return self.validateCaptcha(recaptcha_response, REQUEST)
        return None


InitializeClass(Factsheet)
