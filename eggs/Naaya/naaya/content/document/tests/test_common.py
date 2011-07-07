from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.document.document_item import addNyDocument

class DocumentCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyDocument(parent, title='My document', submitted=1)]
        ob.approveThis()
        return ob
