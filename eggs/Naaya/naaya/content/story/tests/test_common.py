from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.base.tests.common import IconTestsMixin
from naaya.content.story.story_item import addNyStory

class StoryIconTests(IconTestsMixin, NaayaTestCase):

    def add_object(self, parent):
        ob = parent[addNyStory(parent, title='My story', submitted=1)]
        ob.approveThis()
        return ob
