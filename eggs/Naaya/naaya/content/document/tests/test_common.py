from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from naaya.content.document.document_item import addNyDocument

class DocumentIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        ob = parent[addNyDocument(parent, title='My document', submitted=1)]
        ob.approveThis()
        return ob
