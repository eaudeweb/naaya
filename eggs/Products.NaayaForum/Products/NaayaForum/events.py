from zope.interface import implements

from interfaces import (INyForumObjectAddEvent,
                        INyForumTopicAddEvent,
                        INyForumMessageAddEvent,
                        INyForumObjectEditEvent,
                        INyForumTopicEditEvent,
                        INyForumMessageEditEvent)

class BasicEvent(object):
    def __init__(self, context, contributor):
        self.context = context
        self.contributor = contributor

class NyForumObjectAddEvent(BasicEvent):
    implements(INyForumObjectAddEvent)

class NyForumTopicAddEvent(NyForumObjectAddEvent):
    implements(INyForumTopicAddEvent)

class NyForumMessageAddEvent(NyForumObjectAddEvent):
    implements(INyForumMessageAddEvent)

class NyForumObjectEditEvent(BasicEvent):
    implements(INyForumObjectEditEvent)

class NyForumTopicEditEvent(NyForumObjectEditEvent):
    implements(INyForumTopicEditEvent)

class NyForumMessageEditEvent(NyForumObjectEditEvent):
    implements(INyForumMessageEditEvent)
