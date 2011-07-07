from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.pointer.pointer_item import addNyPointer

class PointerCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyPointer(parent, title='My pointer')]
        ob.approveThis()
        return ob
