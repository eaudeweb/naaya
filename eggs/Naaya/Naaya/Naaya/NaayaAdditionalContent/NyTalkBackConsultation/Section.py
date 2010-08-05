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
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
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

    id = base_id = self.utCleanupId(id) or self.utGenObjectId(title)
    i = 0
    while self._getOb(id, None) is not None:
        i += 1
        id = '%s-%d' % (base_id, i)
    ob = Section(id, title, body)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.parseBody()
    if REQUEST is not None:
        self.REQUEST.RESPONSE.redirect(self.absolute_url())


class Section(Folder):
    meta_type = METATYPE_TALKBACKCONSULTATION_SECTION
    security = ClassSecurityInfo()

    meta_types = [
        {'name': METATYPE_TALKBACKCONSULTATION_PARAGRAPH, 'action': 'addParagraph',
            'permission': PERMISSION_MANAGE_TALKBACKCONSULTATION},
    ]

    def __init__(self, id, title, body):
        self.id =  id
        self.title = title
        self.body = body
        self.next_available_id = 0 # some legacy Section instances might not have this attribute
        self.paragraph_ids = [] # some legacy Section instances might not have this attribute

    def _ensure_paragraph_ids(self):
        """
        Make sure this Section instance has the paragraph_ids list
        attached to it (some legacy objects don't have it)
        """
        if getattr(self, 'paragraph_ids', None) is None:
            self.paragraph_ids = [p.id for p in  self.objectValues(
                    [METATYPE_TALKBACKCONSULTATION_PARAGRAPH])]
            self._p_changed = 1

    security.declareProtected(view, 'get_section')
    def get_section(self):
        return self

    security.declarePrivate('make_paragraph_id')
    def make_paragraph_id(self):
        next_id = getattr(self, 'next_available_id', None)
        if next_id is None:
            # this must be an old Section instance
            self._ensure_paragraph_ids()
            next_id = int( list(self.paragraph_ids)[-1] ) + 1
        self.next_available_id = next_id + 1
        return '%03d' % next_id

    security.declarePrivate('remove_paragraph')
    def remove_paragraph(self, paragraph_id):
        self._ensure_paragraph_ids()
        self.manage_delObjects([paragraph_id])
        self.paragraph_ids.remove(paragraph_id)
        self._p_changed = 1

    security.declareProtected(view, 'get_paragraphs')
    def get_paragraphs(self):
        self._ensure_paragraph_ids()
        for p in self.paragraph_ids:
            yield self._getOb(p)

    security.declareProtected(view, 'get_previous_section')
    def get_previous_section(self):
        sections = self.list_sections()
        i = sections.index(self)
        if i > 0:
            return sections[i-1]
        else:
            return None

    security.declareProtected(view, 'get_next_section')
    def get_next_section(self):
        sections = self.list_sections()
        i = sections.index(self)
        if i+1 < len(sections):
            return sections[i+1]
        else:
            return None

    security.declareProtected(view, 'comment_count')
    def comment_count(self):
        return sum(p.comment_count() for p in self.get_paragraphs())

    security.declarePrivate('parseBody')
    def parseBody(self):
        output = parse(self.body)
        for paragraph in output:
            addParagraph(self, body=paragraph)

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'saveProperties')
    def saveProperties(self, title, REQUEST=None):
        """ """
        self.title = title
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit_html')

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/section_edit', globals())

    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/section_index', globals(),
                                       'tbconsultation_section_index')

    security.declareProtected(view, 'section_js')
    section_js = ImageFile('www/section.js', globals())

InitializeClass(Section)
