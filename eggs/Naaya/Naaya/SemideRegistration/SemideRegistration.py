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
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
import re
import time

from utilities.Slugify import slugify

add_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_registration(self, id='', title='', administrative_email ='', start_date='', end_date='', introduction='', REQUEST=None):
    """ Adds a Semide registration instance"""
    if registration_validation(REQUEST):
        if not id:
            id = slugify(title)
        ob = SemideRegistration(id, title, administrative_email, start_date, end_date, introduction)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

def registration_validation(REQUEST):
    """ Validates the new meeting registration fields """
    has_errors = False

    title = REQUEST.form.get('title', '')
    administrative_email = REQUEST.form.get('administrative_email', '')
    start_date = REQUEST.form.get('start_date', '')
    end_date = REQUEST.form.get('end_date', '')

    if not title:
        REQUEST.set('title_error', True)
        has_errors = True
    if not administrative_email:
        REQUEST.set('administrative_email_error', True)
        has_errors = True
    if not start_date:
        REQUEST.set('start_date_error', True)
        has_errors = True
    if not end_date:
        REQUEST.set('end_date_error', True)
        has_errors = True
    if administrative_email and not email_expr.match(administrative_email):
        REQUEST.set('administrative_email_invalid', True)
        has_errors = True
    if start_date:
        try:
            date = time.strptime(start_date, "%d/%m/%Y")
        except:
            REQUEST.set('start_date_invalid', True)
            has_errors = True
    if end_date:
        try:
            date = time.strptime(end_date, "%d/%m/%Y")
        except:
            REQUEST.set('end_date_invalid', True)
            has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

class SemideRegistration(Folder):
    """ Main class of the meeting registration"""

    meta_type = 'Semide Registration'
    product_name = 'SemideRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title, administrative_email, start_date, end_date, introduction):
        """ constructor """
        self.id = id
        self.title = title
        self.administrative_email = administrative_email
        self.start_date = start_date
        self.end_date = end_date
        self.introduction = introduction

    registration = PageTemplateFile('zpt/registration/registration', globals())
    registration_press = PageTemplateFile('zpt/registration/registration_press', globals())


InitializeClass(SemideRegistration)