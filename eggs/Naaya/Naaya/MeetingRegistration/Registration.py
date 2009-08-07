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
from AccessControl.Permissions import view_management_screens, view
from urllib import quote
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Formulator.Form import manage_add as manage_addZMIForm
from Slugify import slugify
from constants import *

manage_addRegistration_html = PageTemplateFile('zpt/registration_add', globals())
def manage_addRegistration(self, title='', REQUEST=None):
    """ """
    if not title:
        raise ValueError('The title is mandatory')
    id = slugify(title)
    ob = Registration(id, title)
    self._setObject(id, ob)
    ob = self._getOb(id)
    manage_addZMIForm(ob, 'registration',unicode_mode=1)

#    if REQUEST is not None:
#        return self.manage_main(self, REQUEST, update_menu=1)
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    u = "%s/%s" % (u, quote(id))
#    return ob.form_edit_html(REQUEST, field_types = field_types)
    REQUEST.RESPONSE.redirect(u+'/index_html')

class Registration(Folder):
    meta_type = 'Meeting registration'
    product_name = 'MeetingRegistration'

    def __init__(self, id, title, index_title='Participants registration'):
        """ constructor """
        self.id = id
        self.title = title
        self.index_title = index_title
        self.introduction = ''
        self.start_date = ''
        self.end_date = ''

    index_html = PageTemplateFile('zpt/index', globals())
    index_edit_html = PageTemplateFile('zpt/index_edit', globals())

    def save_index(self, REQUEST):
        """ method for saving the content of the index """
        request = REQUEST.form.get
        self.index_title = request('index_title')
        self.start_date = request('start_date')
        self.end_date = request('end_date')
        self.introduction = request('introduction')
        REQUEST.RESPONSE.redirect('index_html')

    def newlineToBr(self, text):
        """ """
        if text.find('\r') >= 0: text = ''.join(text.split('\r'))
        if text.find('\n') >= 0: text = '<br />'.join(text.split('\n'))
        return text

    def manage_addField(self, REQUEST):
        """ """
        request = REQUEST.form.get
        id = request('id')
        label = request('label')
        field_type = request('field_type')
        self.registration.manage_addField (id, label, field_type)
        self.registration._getOb(id).manage_edit(REQUEST)
        REQUEST.RESPONSE.redirect('index_html')

    _form_edit_html = PageTemplateFile('zpt/form_edit', globals())
    def form_edit_html(self, REQUEST):
        """ """
        return self._form_edit_html(REQUEST, field_types = field_types)