#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit

#Product imports
from parser import parse
from Section import addSection


addChapter_html = PageTemplateFile('zpt/chapter_add', globals())
def addChapter(self, id='', title='', body='', REQUEST=None):
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    ob = Chapter(id, title, body)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.parseBody()


class Chapter(Folder):

    meta_type = 'TalkBack Chapter'
    all_meta_types = ()
    security = ClassSecurityInfo()

    def __init__(self, id, title, body):
        self.id =  id
        self.title = title
        self.body = body

    def get_sections(self):
        return self.objectValues(['TalkBack Section'])

    def parseBody(self):
        output = parse(self.body)
        i = 0
        for section in output:
            id = '%03d' % i
            addSection(self, id, body=section)
            i += 1

    def get_chapter(self):
        return self

    edit_html = PageTemplateFile('zpt/chapter_edit', globals())
    index_html = PageTemplateFile('zpt/chapter_index', globals())


InitializeClass(Chapter)