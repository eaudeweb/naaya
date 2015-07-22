from zope.interface import implements
from interfaces import ICSVImportEvent


class CSVImportEvent(object):
    """Event triggered after a naaya content object has been added
    """
    implements(ICSVImportEvent)

    def __init__(self, context, ids):
        self.context = context
        self.ids = ids
