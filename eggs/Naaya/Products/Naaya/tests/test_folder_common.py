from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from Products.Naaya.NyFolder import addNyFolder

class FolderIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        addNyFolder(parent, 'myfol', contributor='contributor', submitted=1)
        parent['myfol'].approveThis()
        return parent['myfol']
