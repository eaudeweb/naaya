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

from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import time
import re

new_registration = PageTemplateFile('zpt/registration_form/index', globals())
view = PageTemplateFile('zpt/registration_form/view', globals())

def view_participant(self, participant_id):
    return view.__of__(self)(participant_id=participant_id)

def registration(self, list_name, REQUEST):
    if REQUEST.REQUEST_METHOD == "POST":
        form_list = self.get_list_by_name(list_name)
        if new_registration_validation(form_list, REQUEST):
            participant_id = addParticipant(self, list_name, REQUEST)
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/view_participant?participant_id=%s' % participant_id)
            #return view_participant(self, participant_id)
    return new_registration.__of__(self)(REQUEST, list_name=list_name)

def addParticipant(self, list_name, REQUEST):
    """ Adds a participant's profile"""
    from random import randrange
    
    form_list = self.get_list_by_name(list_name)
    profile_type = (list_name == 'form_edit_participants') and 'participant_' or 'press_'
    form_fields = [field.id for field in form_list]
    id = profile_type + str(randrange(1000000,9999999))
    newParticipant = Participant(id, form_fields, **REQUEST.form)
    self._setObject(id, newParticipant)
    return id

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

def new_registration_validation(form_list, REQUEST):
    """ """
    has_errors = False
    mandatory_fields = []
    for field in form_list:
        if field.mandatory:
            mandatory_fields.append(field.id)
    for id in mandatory_fields:
        if id not in REQUEST.form or not REQUEST.form.get(id):
            REQUEST.set('%s_error' % id, True)
            has_errors = True
    for field in form_list:
        if field.field_type == 'email_field':
            value = REQUEST.form.get(field.id)
            if not email_expr.match(value):
                REQUEST.set('%s_invalid' % field.id, True)
                has_errors = True
        if field.field_type == 'date_field':
            value = REQUEST.form.get(field.id)
            try:
                value and time.strptime(value, "%d/%m/%Y")
            except:
                REQUEST.set('%s_invalid' % field.id, True)
                has_errors = True
        if field.field_type == 'time_field':
            value = REQUEST.form.get(field.id)
            try:
                value and time.strptime(value, "%H:%M")
            except:
                REQUEST.set('%s_invalid' % field.id, True)
                has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

class Participant(SimpleItem):
    """ Defines the profile of a registered participant,
    based on the fields of the meeting registration form"""

    meta_type = 'Participant Profile'

    def __init__(self, id, form_fields, **kwargs):
        """ """
        self.id = id
        for k in form_fields:
            if kwargs.has_key(k):
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, '')
            #procesari (date = datetime(v))

InitializeClass(Participant)