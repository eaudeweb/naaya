from naaya.content.base.tests.common import _IconTests
from naaya.content.document.document_item import addNyDocument

class DocumentIconTests(_IconTests):

    def add_object(self, parent):
        ob = parent[addNyDocument(parent, title='My document', submitted=1)]
        ob.approveThis()
        return ob
