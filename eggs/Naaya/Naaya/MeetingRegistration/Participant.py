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
from DateTime import DateTime

def addParticipant(self, REQUEST):
    """ Adds a participant's profile"""
    from random import randrange
    
    list_name = REQUEST.form.get('list_name')
    form_list = self.get_list_by_name(list_name)
    profile_type = (list_name == 'form_edit_participants') and 'participant_' or 'press_'
    mandatory_fields = []
    for field in form_list:
        if field.mandatory:
            mandatory_fields.append(field.id)
    if not new_registration_validation(self, list_name, mandatory_fields, REQUEST):
        return (list_name == 'form_edit_participants') and self.registration_participants() or self.registration_press()
    form_fields = [field.id for field in form_list]
    newParticipant = Participant(form_fields, **REQUEST.form)
    id = profile_type + str(randrange(1000000,9999999))
    self._setObject(id, newParticipant)
    #Redirect to confirmation / print

def new_registration_validation(self, list_name, mandatory_fields, REQUEST):
    """ """
    has_errors = False
    for id in mandatory_fields:
        if id not in REQUEST.form or not REQUEST.form.get(id):
            REQUEST.set('%s_error' % id, True)
            has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

class Participant(SimpleItem):
    """ Defines the profile of a registered participant,
    based on the fields of the meeting registration form"""
    def __init__(self, form_fields, **kwargs):
        """ """
        for k in form_fields:
            if kwargs.has_key(k):
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, '')
            #procesari (date = datetime(v))

InitializeClass(Participant)