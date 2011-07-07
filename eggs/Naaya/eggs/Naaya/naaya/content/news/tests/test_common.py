from naaya.content.base.tests.common import _IconTests
from naaya.content.news.news_item import addNyNews

class NewsIconTests(_IconTests):

    def add_object(self, parent):
        ob = parent[addNyNews(parent, title='My news')]
        ob.approveThis()
        return ob
