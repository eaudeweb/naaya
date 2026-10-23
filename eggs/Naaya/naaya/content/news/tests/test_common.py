from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from naaya.content.news.news_item import addNyNews

class NewsIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        ob = parent[addNyNews(parent, title='My news')]
        ob.approveThis()
        return ob
