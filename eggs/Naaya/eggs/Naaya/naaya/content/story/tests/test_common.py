from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.story.story_item import addNyStory

class StoryCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyStory(parent, title='My story', submitted=1)]
        ob.approveThis()
        return ob
