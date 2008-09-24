#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit

#Product imports
from comment_item import addComment

addSection_html = PageTemplateFile('zpt/section_add', globals())

def addSection(self, id='', title='', body='', REQUEST=None):
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    ob = Section(id, title, body)
    self._setObject(id, ob)


class Section(Folder):

    meta_type = 'TalkBack Section'
    #all_meta_types = ()
    security = ClassSecurityInfo()

    def __init__(self, id, title, body):
        self.id =  id
        self.title = title
        self.body = body

    def get_anchor(self):
        return 'naaaya-talkback-section-%s' % self.id

    def get_comments(self):
        return self.objectValues(['TalkBack Consultation Comment'])

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

    addComment = addComment

    #forms
    index_html = PageTemplateFile('zpt/section_index', globals())
    comment_added = PageTemplateFile('zpt/comment_added', globals())

InitializeClass(Section)