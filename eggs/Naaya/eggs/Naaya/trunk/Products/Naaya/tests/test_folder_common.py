from naaya.content.base.tests.common import _IconTests
from Products.Naaya.NyFolder import addNyFolder

class FolderIconTests(_IconTests):

    def add_object(self, parent):
        addNyFolder(parent, 'myfol', contributor='contributor', submitted=1)
        parent['myfol'].approveThis()
        return parent['myfol']
