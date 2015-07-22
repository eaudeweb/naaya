from zope.interface import implements
from interfaces import ICSVImportEvent
from interfaces import IZipImportEvent


class CSVImportEvent(object):
    """Event triggered after a naaya content object has been added
    """
    implements(ICSVImportEvent)

    def __init__(self, context, ids):
        self.context = context
        self.ids = ids


class ZipImportEvent(object):
    """Event triggered after a successful zip upload
    """

    implements(IZipImportEvent)

    def __init__(self, context, zip_contents):
        self.context = context
        self.zip_contents = zip_contents
