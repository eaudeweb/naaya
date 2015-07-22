from naaya.content.base.tests.common import _IconTests
from naaya.content.url.url_item import addNyURL

class UrlIconTests(_IconTests):

    def add_object(self, parent):
        ob = parent[addNyURL(parent, title='My url')]
        ob.approveThis()
        return ob
