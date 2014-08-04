from naaya.content.base.tests.common import _IconTests
from naaya.content.event.event_item import addNyEvent

class EventIconTests(_IconTests):

    def add_object(self, parent):
        kwargs = {'title': 'My event', 'start_date': "10/10/2000"}
        ob = parent[addNyEvent(parent, **kwargs)]
        ob.approveThis()
        return ob
