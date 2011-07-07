from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.news.news_item import addNyNews

class News(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyNews(parent, title='My news')]
        ob.approveThis()
        return ob
