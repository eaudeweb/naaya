from naaya.content.base.tests.common import _IconTests
from naaya.content.pointer.pointer_item import addNyPointer

class PointerIconTests(_IconTests):

    def add_object(self, parent):
        ob = parent[addNyPointer(parent, title='My pointer')]
        ob.approveThis()
        return ob
