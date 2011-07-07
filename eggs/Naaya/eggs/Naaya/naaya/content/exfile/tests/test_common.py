from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.exfile.exfile_item import addNyExFile

class ExFileCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyExFile(parent, title='My exfile')]
        ob.approveThis()
        return ob
