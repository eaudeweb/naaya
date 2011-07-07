from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.url.url_item import addNyURL

class UrlCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyURL(parent, title='My url')]
        ob.approveThis()
        return ob
