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
# David Batranu, Eau de Web
# Alex Morega, Eau de Web

#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile
from Acquisition import Implicit

#Product imports
from parser import parse
from Paragraph import addParagraph
from constants import *


addSection_html = PageTemplateFile('zpt/section_add', globals())
def addSection(self, id='', title='', body='', REQUEST=None):
    """ """

    errors = []
    if not title:
        errors.append('The title field must have a value')
    if not body:
        errors.append('The section must have a body')
    if errors:
        self.setSessionErrors(errors)
        if REQUEST is not None:
            self.setSession('title', title)
            self.setSession('body', body)
            self.REQUEST.RESPONSE.redirect(self.absolute_url() +
                                           '/section_add_html')
        return
    self.delSession('title')
    self.delSession('body')

    id = self.utCleanupId(id)
    if not id: id = '%s-%s' % (self.utGenObjectId(title), self.utGenRandomId(6))
    ob = Section(id, title, body)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.parseBody()
    if REQUEST is not None:
        self.REQUEST.RESPONSE.redirect(self.absolute_url())


class Section(Folder):
    meta_type = METATYPE_TALKBACKCONSULTATION_SECTION
    all_meta_types = ()
    security = ClassSecurityInfo()

    def __init__(self, id, title, body):
        self.id =  id
        self.title = title
        self.body = body

    security.declareProtected(view, 'get_section')
    def get_section(self):
        return self

    security.declareProtected(view, 'get_paragraphs')
    def get_paragraphs(self):
        return self.objectValues([METATYPE_TALKBACKCONSULTATION_PARAGRAPH])

    security.declarePrivate('parseBody')
    def parseBody(self):
        output = parse(self.body)
        i = 0
        for paragraph in output:
            id = '%03d' % i
            addParagraph(self, id, body=paragraph)
            i += 1

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/section_edit', globals())

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/section_index', globals())

    security.declareProtected(view, 'jquery_js')
    jquery_js = ImageFile('www/jquery.js', globals())

    security.declareProtected(view, 'chapter_js')
    chapter_js = ImageFile('www/chapter.js', globals())

InitializeClass(Section)
