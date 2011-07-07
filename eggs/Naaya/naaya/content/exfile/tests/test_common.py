from nose import SkipTest
from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.exfile.exfile_item import addNyExFile

class ExFileCommonTest(_CommonContentTest):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya Extended File')
        ob = parent[addNyExFile(parent, title='My exfile')]
        ob.approveThis()
        return ob

    def test_icon(self):
        raise SkipTest

    def test_customized_icon(self):
        raise SkipTest
