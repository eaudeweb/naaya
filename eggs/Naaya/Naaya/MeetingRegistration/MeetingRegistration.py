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
from persistent.list import PersistentList
from Globals import Persistent
from operator import attrgetter


from utilities.Slugify import slugify
from Constants import *
import Participant

from DateTime import DateTime

add_registration = PageTemplateFile('zpt/meeting_registration/add', globals())

def manage_add_registration(self, id='', title='', administrative_email ='', start_date='', end_date='', introduction='', REQUEST=None):
    """ Adds a meeting registration instance"""
    if registration_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
        if not id:
            id = slugify(title)
        ob = MeetingRegistration(id, title, administrative_email, start_date, end_date, introduction)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

def registration_validation(mandatory_fields, REQUEST, **kwargs):
    """ Validates the new meeting registration fields """
    has_errors = False
    for k,v in kwargs.items():
        if k in mandatory_fields:
            if (k == 'administrative_email') and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_invalid' % k, True)
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
    """ Main class of the meeting registration"""

    meta_type = 'Meeting registration'
    product_name = 'MeetingRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title, administrative_email, start_date, end_date, introduction):
        """ constructor """
        self.id = id
        self.title = title
        self.administrative_email = administrative_email
        self.start_date = start_date
        self.end_date = end_date
        self.introduction = introduction
        self.registration_form_participants = PersistentList()
        self.registration_form_press = PersistentList()

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'view_participant')
    def view_participant(self, REQUEST):
        """ """
        participant_id = REQUEST.get('participant_id', '')
        return Participant.view_participant(self, participant_id)

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'get_participant')
    def get_participant(self, participant_id):
        """ """
        for participant in self.objectValues('Participant Profile'):
            if participant.id == participant_id:
                return participant
        return None

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'registration_participants')
    def registration_participants(self, REQUEST):
        """ """
        return Participant.registration(self, 'form_edit_participants', REQUEST)

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'registration_press')
    def registration_press(self, REQUEST):
        """ """
        return Participant.registration(self, 'form_edit_press', REQUEST)

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'index_html')
    index_html = PageTemplateFile('zpt/meeting_registration/index', globals())

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'view_participants')
    view_participants = PageTemplateFile('zpt/meeting_registration/overview_participants', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'edit')
    edit = PageTemplateFile('zpt/meeting_registration/edit', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'manage_edit_registration')
    def manage_edit_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
        """ Edits the properties of the meeting registration """
        if registration_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
            self.title = title
            try:
                start_date = DateTime(start_date)
            except:
                eroare
            if not end_date > start_date:
                eroare
            self.start_date = start_date
            self.end_date = end_date
            self.introduction = introduction
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url())
        else:
            return self.edit(REQUEST)

    security.declareProtected(EDIT_MEETING_REGISTRATION, '_form_edit')
    _form_edit = PageTemplateFile('zpt/registration_form/edit', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'form_edit_participants')
    def form_edit_participants(self, REQUEST):
        """ Call the edit form for participants"""
        return self.form_edit('form_edit_participants', REQUEST)

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'form_edit_press')
    def form_edit_press(self, REQUEST):
        """ Call the edit form for press"""
        return self.form_edit('form_edit_press', REQUEST)

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'form_edit')
    def form_edit(self, list_name, REQUEST):
        """ Edits the registration form, as it will be viewed by the participants"""
        form_list = self.get_list_by_name(list_name)
        id = REQUEST.get('edit_field_id', '')
        if id:
            field_index = self.return_index(form_list, id)
            field = form_list[field_index]
            REQUEST.set('field_id', field.id)
            REQUEST.set('field_type', field.field_type)
            REQUEST.set('field_label', field.field_label)
            REQUEST.set('field_content', field.field_content)
            REQUEST.set('mandatory', field.mandatory)
            REQUEST.set('overview', field.overview)
        REQUEST.set('list_name', list_name)
        return self._form_edit(REQUEST, field_types = field_types)

    #interface API
    def list_fields(self, list_name):
        """ returns fields list """
        form_list = self.get_list_by_name(list_name)
        return [ field for field in form_list if field.overview]

    def list_participants(self, skey, rkey, ptype="participant"):
        """ Returns the participants list, filtered and sorted according with the given parameters. """
        participants = [ (getattr(p, skey, 'id'), p) for p in self.objectValues('Participant Profile') if p.id.startswith(ptype) ]
        participants.sort()
        if rkey:
            participants.reverse()
        return [p for (key, p) in participants]

    def getFieldValue(self, ob, id):
        """ returns the field value for a given object and field """
        return getattr(ob , id, '')

    def get_list_by_name(self, list_name):
        if list_name == 'form_edit_participants':
            return self.registration_form_participants
        if list_name == 'form_edit_press':
            return self.registration_form_press
        raise ValueError ('Unknown list name "%s"' % list_name)

    def get_field_by_id(self, list_name, id):
        form_list = self.get_list_by_name(list_name)
        for item in form_list:
            if item.id == id: return item
        raise ValueError ('Inexistent id "%s" ' % id)

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'manage_addField')
    def manage_addField(self, REQUEST):
        """ Adds a new field to the registration form """
        list_name = REQUEST.form.get('list_name', '')
        form_list = self.get_list_by_name(list_name)
        from random import randrange
        if self.field_validation(mandatory_fields_field, REQUEST):
            request = REQUEST.form.get
            id = request('field_id', '')
            if not id:
                id = str(randrange(1000000,9999999))
            field_type = request('field_type')
            field_label = request('field_label')
            field_content = request('field_content', '')
            selection_values = request('selection_values', '')
            mandatory = request('mandatory', False)
            overview = request('overview', False)
            field_index = self.return_index(form_list, id)
            if field_index is not None:
                form_list[field_index] = FormField(id, field_type, field_label, field_content, selection_values, mandatory, overview)
            else:
                form_list.append(FormField(id, field_type, field_label, field_content, selection_values, mandatory, overview))
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url()+'/%s' % list_name)
                #return self.form_edit(None)
        else:
            return self.form_edit(list_name, REQUEST)

    def get_field_label(self, list_name, id):
        """ Returns the field label based on the field id """
        form_list = self.get_list_by_name(list_name)
        return form_list[self.return_index(form_list, id)].field_label

    def return_index(self, form_list, id):
        for field in form_list:
            if field.id == id:
                return form_list.index(field)
        return None

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'delete_field')
    def delete_field(self, id, REQUEST):
        """ deletes selected (id) field """
        list_name = REQUEST.form.get('list_name', '')
        form_list = self.get_list_by_name(list_name)
        del form_list[self.return_index(form_list, id)]
        #return REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')
        REQUEST.set('delete_field_id', '')
        REQUEST.set('field_deleted', True)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/%s' % list_name)

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'move_up_field')
    def move_up_field(self, id, REQUEST):
        """ Moves the selected field up in the display order """
        list_name = REQUEST.form.get('list_name', '')
        form_list = self.get_list_by_name(list_name)
        field_index  = self.return_index(form_list, id)
        if field_index == 0:
            return
        temp_field = form_list[field_index]
        form_list[field_index] = form_list[field_index - 1]
        form_list[field_index - 1] = temp_field
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/%s' % list_name)

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'move_down_field')
    def move_down_field(self, id, REQUEST):
        """ Moves the selected field down in the display order """
        list_name = REQUEST.form.get('list_name', '')
        form_list = self.get_list_by_name(list_name)
        field_index = self.return_index(form_list, id)
        if field_index == len(form_list) - 1:
            return
        temp_field = form_list[field_index]
        form_list[field_index] = form_list[field_index + 1]
        form_list[field_index + 1] = temp_field
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/%s' % list_name)

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'field_validation')
    def field_validation(self, mandatory_fields, REQUEST):
        """ Validates the field properties before adding a new field to the registration form """
        has_errors = False
        for field in mandatory_fields:
            if field not in REQUEST.form or not REQUEST.form.get(field):
                REQUEST.set('%s_error' % field, True)
                has_errors = True
            if REQUEST.form.get('field_type') == 'body_text' and not REQUEST.form.get('field_content'):
                REQUEST.set('body_text_error', True)
                has_errors = True
            if REQUEST.form.get('field_type') == 'selection_field' and not REQUEST.form.get('selection_values'):
                REQUEST.set('selection_field_error', True)
                has_errors = True
        if has_errors:
            REQUEST.set('request_error', True)
        return not has_errors

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'field_ids')
    def field_ids(self, list_name='', participant_id=''):
        """ returns a list with the field ids, based on the list name or on the participant's id"""
        if not list_name:
            if not participant_id:
                raise ValueError ('field_ids function called with no list name and no participant id')
            if participant_id.split('_')[0] == 'participant':
                list_name = 'form_edit_participants'
            else:
                list_name = 'form_edit_press'
        form_list = self.get_list_by_name(list_name)
        return [field.id for field in form_list]

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'error_message')
    def error_message(self, list_name, id, type):
        """ Renders the error message if a field is not validated """
        field = self.get_field_by_id(list_name, id)
        if type == 'error':
            return '<tr><td colspan="4">The field %s is mandatory!</td></tr>' % field.field_label
        if type == 'invalid':
            return '<tr><td colspan="4">Please fill the field %s correctly!</td></tr>' % field.field_label
        return ''

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'render_fields')
    def render_profile(self, id):
        """ Displays the data in a registrated profile """
        participant = self.get_participant(id)
        html_code = ''
        if id.split('_')[0] == 'participant':
            list_name = 'form_edit_participants'
        else:
            list_name = 'form_edit_press'
        form_list = self.get_list_by_name(list_name)
        for field in form_list:
            html_code += '<dt i18n:translate="">%s</dt><dd>%s</dd>' % (field.field_label, getattr(participant, field.id, ''))
        return html_code

    def render_fields(self, REQUEST, list_name, id, is_editing = False):
        """ Renders the fields of the registration form """
        form_list = self.get_list_by_name(list_name)
        field = self.get_field_by_id(list_name, id)
        html_code = ''

        #Buttons
        edit_link = self.absolute_url()+'/%s?edit_field_id=' % list_name +field.id
        delete_link  = self.absolute_url()+'/%s?delete_field_id=' % list_name +field.id
        move_up_link  = self.absolute_url()+'/move_up_field?list_name=%s&id=%s'% (list_name, field.id)
        move_down_link  = self.absolute_url()+'/move_down_field?list_name=%s&id=%s'% (list_name, field.id)

        #Label, red for mandatory fields
        if field.mandatory:
            label = '<td><label for="%s" i18n:translate="" style="color: #f40000">%s</label></td>' % (field.id, field.field_label)
        else:
            label = '<td><label for="%s" i18n:translate="">%s</label></td>' % (field.id, field.field_label)

        #Render the different types of fields
        input_field = '<td><input id="%s" name="%s:utf8:ustring" type="text" size="50" value="%s"/></td>' % (field.id, field.id, REQUEST.get(field.id, ''))
        input_date = '''<td><input id="%s" name="%s" class="vDateField" type="text" size="10" maxlength="10" value="%s"/>
        <noscript><em class="tooltips">(dd/mm/yyyy)</em></noscript></td>''' % (field.id, field.id, REQUEST.get(field.id, ''))
        input_time = '''<td><input id="%s" name="%s" type="text" size="10" maxlength="5" value="%s"/>
        <noscript><em class="tooltips">(HH:MM)</em></noscript></td>''' % (field.id, field.id, REQUEST.get(field.id, ''))
        input_checkbox = '<td><input id="%s" name="%s" type="checkbox" value="%s"/></td>' % (field.id, field.id, REQUEST.get(field.id, ''))
        input_selection_values = ''
        for value in field.selection_values:
            input_selection_values += '<input type="radio" name="%s" value="%s"/>%s<br/>' % (field.id, value, value)
        input_selection = '<td>' + input_selection_values + '</td>'
        textarea = '<td><textarea class="mceNoEditor" id="%s" name="%s:utf8:ustring" type="text" rows="5" cols="50" >%s</textarea></td>' % (field.id, field.id, REQUEST.get(field.id, ''))
        body_text = '<td colspan="2">%s</td>' % field.field_content

        if is_editing:
            if len(form_list) == 1:
                buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td>' % (edit_link, delete_link)
            elif field == form_list[0]:
                buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td></td><td><span class="buttons"><a href="%s">Move down</a></span></td>' % (edit_link, delete_link, move_down_link)
            elif field == form_list[-1]:
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
        if field.field_type == 'time_field':
            html_code = html_code + '<tr>' + label + input_time + buttons + '</tr>'
        if field.field_type == 'checkbox_field':
            html_code = html_code + '<tr>' + label + input_checkbox + buttons + '</tr>'
        if field.field_type == 'body_text':
            html_code = html_code + '<tr>' + body_text + buttons + '</tr>'
        if field.field_type == 'selection_field':
            html_code = html_code + '<tr>' + label + input_selection + buttons + '</tr>'
        return html_code

InitializeClass(MeetingRegistration)

class FormField(Persistent):
    ''' Defines the properties of a meeting registration field'''

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, id, field_type, field_label, field_content, selection_values, mandatory, overview):
        self.id = id
        self.field_type = field_type
        self.field_label = field_label
        self.field_content = field_content
        self.mandatory = mandatory
        self.overview = overview
        self.selection_values = selection_values

InitializeClass(FormField)
