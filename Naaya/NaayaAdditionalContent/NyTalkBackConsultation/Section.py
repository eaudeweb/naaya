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
from Acquisition import Implicit

#Product imports
from comment_item import addComment
from constants import *


def addSection(self, id='', title='', body='', REQUEST=None):
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    ob = Section(id, title, body)
    self._setObject(id, ob)


class Section(Folder):

    meta_type = METATYPE_TALKBACKCONSULTATION_SECTION

    security = ClassSecurityInfo()

    def all_meta_types( self, interfaces=None ):
        """
        Called by Zope to determine what
        kind of object the envelope can contain
        """
        return [{'name': METATYPE_TALKBACKCONSULTATION_COMMENT,
              'action': 'addComment',
              'permission': PERMISSION_REVIEW_TALKBACKCONSULTATION}
             ]


    def __init__(self, id, title, body):
        self.id =  id
        self.title = title
        self.body = body

    def get_anchor(self):
        return 'naaaya-talkback-section-%s' % self.id

    def get_comments(self):
        return self.objectValues([METATYPE_TALKBACKCONSULTATION_COMMENT])

    def merge_down(self):
        """ """
        sections = [section.id for section in self.get_sections()]
        sections.sort()
        try:
            next_section = sections[sections.index(self.id)+1]
            next_section = self.get_chapter()._getOb(next_section)
        except IndexError:
            return

        self.body += next_section.body

        comment_ids = [comment.getId() for comment in next_section.get_comments()]
        objs = next_section.manage_copyObjects(comment_ids)
        self.manage_pasteObjects(objs)

        self.get_chapter().manage_delObjects([next_section.id])

    security.declareProtected(PERMISSION_REVIEW_TALKBACKCONSULTATION, 'addComment')
    addComment = addComment

    #forms
    index_html = PageTemplateFile('zpt/section_index', globals())
    comment_added = PageTemplateFile('zpt/comment_added', globals())

InitializeClass(Section)
