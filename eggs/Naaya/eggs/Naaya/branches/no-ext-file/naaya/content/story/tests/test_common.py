from naaya.content.base.tests.common import _IconTests
from naaya.content.story.story_item import addNyStory

class StoryIconTests(_IconTests):

    def add_object(self, parent):
        ob = parent[addNyStory(parent, title='My story', submitted=1)]
        ob.approveThis()
        return ob
