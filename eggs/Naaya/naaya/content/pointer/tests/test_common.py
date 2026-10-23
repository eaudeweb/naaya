from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from naaya.content.pointer.pointer_item import addNyPointer

class PointerIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        ob = parent[addNyPointer(parent, title='My pointer')]
        ob.approveThis()
        return ob
