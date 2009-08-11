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

import re
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from utilities.Slugify import slugify
from Constants import *


add_registration = PageTemplateFile('zpt/meeting_registration/add', globals())
def manage_add_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
    """ """
    if form_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
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

def form_validation (mandatory_fields, REQUEST, **kwargs):
    has_errors = False
    for k,v in kwargs.items():
        if k in mandatory_fields:
            if (k == 'email') and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_notvalid' % k, True)
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

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/meeting_registration/index', globals())

    security.declareProtected(view, 'edit_html')
    edit = PageTemplateFile('zpt/meeting_registration/edit', globals())
    def manage_edit_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
        """ """
        if form_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
            self.title = title
            self.start_date = start_date
            self.end_date = end_date
            self.introduction = introduction
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url())
        else:
            return self.edit(REQUEST)

InitializeClass(MeetingRegistration)
