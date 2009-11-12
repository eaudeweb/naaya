from zope.interface import implements
from interfaces import INyContentObjectAddedEvent


class NyContentObjectAddedEvent(object):
    """Event triggered after a naaya content object has been added
    """
    implements(INyContentObjectAddedEvent)

    def __init__(self, context, schema):
        self.context = context
        self.schema = schema
