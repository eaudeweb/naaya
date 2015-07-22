from zope.interface import implements
from interfaces import INyContentObjectAddEvent
from interfaces import INyContentObjectEditEvent


class NyContentObjectAddEvent(object):
    """ Naaya content object has been created """
    implements(INyContentObjectAddEvent)

    def __init__(self, context, contributor, schema_data):
        self.context = context
        self.contributor = contributor
        self.schema = schema_data


class NyContentObjectEditEvent(object):
    """ Naaya content object has been edited """
    implements(INyContentObjectEditEvent)

    def __init__(self, context, contributor):
        self.context = context
        self.contributor = contributor
