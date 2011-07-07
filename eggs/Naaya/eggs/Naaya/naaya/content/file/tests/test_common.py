from nose import SkipTest
from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.file.file_item import addNyFile

class FileCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyFile(parent, title='My file')]
        ob.approveThis()
        return ob

    def test_icon(self):
        raise SkipTest

    def test_customized_icon(self):
        raise SkipTest
