from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from naaya.content.url.url_item import addNyURL

class UrlIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        ob = parent[addNyURL(parent, title='My url')]
        ob.approveThis()
        return ob
