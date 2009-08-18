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
# Valentin Dumitru, Eau de Web

import re
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from persistent.dict import PersistentDict
from operator import attrgetter


from utilities.Slugify import slugify
from Constants import *
import Participant


add_registration = PageTemplateFile('zpt/meeting_registration/add', globals())
def manage_add_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
    """ """
    if registration_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
        if not id:
            id = slugify(title)
        ob = MeetingRegistration(id, title, start_date, end_date, introduction)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

def registration_validation(mandatory_fields, REQUEST, **kwargs):
    has_errors = False
    for k,v in kwargs.items():
        if k in mandatory_fields:
            if (k == 'email') and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_notvalid' % k, True)
                    has_errors = True
            if k == (('start_date') or (k == 'end_date')) and v:
                try:
                    date = DateTime(v)
                except:
                    REQUEST.set('%s_invalid' % k, True)
                    has_errors = True
            if not v:
                REQUEST.set('%s_error' % k, True)
                has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

class MeetingRegistration(Folder):
    """ """

    meta_type = 'Meeting registration'
    product_name = 'MeetingRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title, start_date, end_date, introduction):
        """ constructor """
        self.id = id
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.introduction = introduction
        self.registration_form = PersistentDict()

    addParticipant = Participant.addParticipant

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'index_html')
    index_html = PageTemplateFile('zpt/meeting_registration/index', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'edit')
    edit = PageTemplateFile('zpt/meeting_registration/edit', globals())
    security.declareProtected(EDIT_MEETING_REGISTRATION, 'manage_edit_registration')
    def manage_edit_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
        """ """
        if registration_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
            self.title = title
            self.start_date = start_date
            self.end_date = end_date
            self.introduction = introduction
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url())
        else:
            return self.edit(REQUEST)

    _form_edit = PageTemplateFile('zpt/registration_form/edit', globals())
    def form_edit(self, REQUEST):
        """ """
        edit_field_id = REQUEST.get('edit_field_id', '')
        if edit_field_id:
            field = self.registration_form[edit_field_id]
            REQUEST.set('field_id', field.id)
            REQUEST.set('field_type', field.field_type)
            REQUEST.set('field_label', field.field_label)
            REQUEST.set('field_content', field.field_content)
            REQUEST.set('mandatory', field.mandatory)
            REQUEST.set('position', field.position)
        return self._form_edit(REQUEST, field_types = field_types)

    def manage_addField(self, REQUEST):
        """ """
        from random import randrange
        
        if self.field_validation(mandatory_fields_field, REQUEST):
            request = REQUEST.form.get
            id = request('field_id', '')
            if not id:
                id = str(randrange(1000000,9999999))
            field_type = request('field_type')
            field_label = request('field_label')
            field_content = request('field_content', '')
            mandatory = request('mandatory', False)
            if request('position'):
                position = int(request('position'))
            else:
                position = len(self.registration_form.keys()) + 1
            self.registration_form[id] = FormField(id, field_type, field_label, field_content, mandatory, position)
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')
                #return self.form_edit(None)
        else:
            return self.form_edit(REQUEST)

    def get_field_label(self, id):
        """ """
        return self.registration_form[id].field_label

    def delete_field(self, id, REQUEST):
        """ """
        del self.registration_form[id]
        #return REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')
        REQUEST.set('delete_field_id', '')
        REQUEST.set('field_deleted', True)
        return self.form_edit(REQUEST)

    def move_up_field(self, id, REQUEST):
        """ """
        fields = sorted(self.registration_form.itervalues(), key = attrgetter('position'))
        current_field = self.registration_form[id]
        if current_field == fields[0]:
            return
        for list_index in range(len(fields)):
            if fields[list_index] == current_field:
                p = current_field.position
                current_field.position = fields[list_index - 1].position
                fields[list_index - 1].position = p
                return self.form_edit(REQUEST)
        return self.form_edit(REQUEST)

    def move_down_field(self, id, REQUEST):
        """ """
        fields = sorted(self.registration_form.itervalues(), key = attrgetter('position'))
        current_field = self.registration_form[id]
        if current_field == fields[:-1]:
            return
        for list_index in range(len(fields)):
            if fields[list_index] == current_field:
                p = current_field.position
                current_field.position = fields[list_index + 1].position
                fields[list_index + 1].position = p
                return self.form_edit(REQUEST)
        return self.form_edit(REQUEST)

    def field_validation(self, mandatory_fields, REQUEST):
        has_errors = False
        for field in mandatory_fields:
            if field not in REQUEST.form or not REQUEST.form.get(field):
                REQUEST.set('%s_error' % field, True)
                has_errors = True
            if REQUEST.form.get('field_type') == 'body_text' and not REQUEST.form.get('field_content'):
                REQUEST.set('body_text_error', True)
                has_errors = True
        if has_errors:
            REQUEST.set('request_error', True)
        return not has_errors

    def render_fields(self, is_editing = False):
        """ """
        html_code = ''
        fields = sorted(self.registration_form.itervalues(), key = attrgetter('position'))
        for field in fields:
            edit_link = self.absolute_url()+'/form_edit?edit_field_id='+field.id
            delete_link  = self.absolute_url()+'/form_edit?delete_field_id='+field.id
            move_up_link  = self.absolute_url()+'/move_up_field?id='+field.id
            move_down_link  = self.absolute_url()+'/move_down_field?id='+field.id
            if field.mandatory:
                label = '<td><label for="%s" i18n:translate="" style="color: #f40000">%s</label></td>' % (field.id, field.field_label)
            else:
                label = '<td><label for="%s" i18n:translate="">%s</label></td>' % (field.id, field.field_label)
            input_field = '<td><input id="%s" name="%s:utf8:ustring" type="text" size="50" /></td>' % (field.id, field.id)
            input_date = '''<td><input id="%s" name="%s" class="vDateField" type="text" size="10" maxlength="10" />
            <noscript><em class="tooltips">(dd/mm/yyyy)</em></noscript></td>''' % (field.id, field.id)
            input_checkbox = '<td><input id="%s" name="%s" type="checkbox" /></td>' % (field.id, field.id)
            textarea = '<td><textarea class="mceNoEditor" id="%s" name="%s:utf8:ustring" type="text" rows="5" cols="50" ></textarea></td>' % (field.id, field.id)
            body_text = '<td colspan="2">%s</td>' % field.field_content
            if is_editing:
                if len(fields) == 1:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td>' % (edit_link, delete_link)
                elif field == fields[0]:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td></td><td><span class="buttons"><a href="%s">Move down</a></span></td>' % (edit_link, delete_link, move_down_link)
                elif field == fields[-1]:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td><span class="buttons"><a href="%s">Move up</a></span></td></td><td>' % (edit_link, delete_link, move_up_link)
                else:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td><span class="buttons"><a href="%s">Move up</a></span></td><td><span class="buttons"><a href="%s">Move down</a></span></td>' % (edit_link, delete_link, move_up_link, move_down_link)
            else:
                buttons = ''

            if field.field_type == 'string_field':
                html_code = html_code + '<tr>' + label + input_field + buttons +'</tr>'
            if field.field_type == 'text_field':
                html_code = html_code + '<tr>' + label + textarea + buttons + '</tr>'
            if field.field_type == 'email_field':
                html_code = html_code + '<tr>' + label + input_field + buttons + '</tr>'
            if field.field_type == 'date_field':
                html_code = html_code + '<tr>' + label + input_date + buttons + '</tr>'
            if field.field_type == 'checkbox_field':
                html_code = html_code + '<tr>' + label + input_checkbox + buttons + '</tr>'
            if field.field_type == 'body_text':
                html_code = html_code + '<tr>' + body_text + buttons + '</tr>'
            """if field.field_type == 'selection_field':
                html_code = html_code + '<tr>' + label + input_selection + buttons + '</tr>'"""
        return html_code

    new_registration = PageTemplateFile('zpt/registration_form/index', globals())

InitializeClass(MeetingRegistration)

class FormField:
    ''' Defines the properties of a meeting registration field'''
    def __init__(self, id, field_type, field_label, field_content, mandatory, position):
        self.id = id
        self.field_type = field_type
        self.field_label = field_label
        self.field_content = field_content
        self.mandatory = mandatory
        self.position = position

InitializeClass(FormField)