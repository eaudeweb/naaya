from zope.interface import implementer

from .interfaces import (INyForumObjectAddEvent,
                        INyForumTopicAddEvent,
                        INyForumMessageAddEvent,
                        INyForumObjectEditEvent,
                        INyForumTopicEditEvent,
                        INyForumMessageEditEvent)

class BasicEvent(object):
    def __init__(self, context, contributor):
        self.context = context
        self.contributor = contributor

@implementer(INyForumObjectAddEvent)
class NyForumObjectAddEvent(BasicEvent):
    pass

@implementer(INyForumTopicAddEvent)
class NyForumTopicAddEvent(NyForumObjectAddEvent):
    pass

@implementer(INyForumMessageAddEvent)
class NyForumMessageAddEvent(NyForumObjectAddEvent):
    pass

@implementer(INyForumObjectEditEvent)
class NyForumObjectEditEvent(BasicEvent):
    pass

@implementer(INyForumTopicEditEvent)
class NyForumTopicEditEvent(NyForumObjectEditEvent):
    pass

@implementer(INyForumMessageEditEvent)
class NyForumMessageEditEvent(NyForumObjectEditEvent):
    pass
