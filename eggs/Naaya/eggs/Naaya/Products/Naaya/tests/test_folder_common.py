from naaya.content.base.tests.common import _CommonContentTest
from Products.Naaya.NyFolder import addNyFolder

class FolderCommonTest(_CommonContentTest):

    def add_object(self, parent):
        addNyFolder(parent, 'myfol', contributor='contributor', submitted=1)
        parent['myfol'].approveThis()
        return parent['myfol']
