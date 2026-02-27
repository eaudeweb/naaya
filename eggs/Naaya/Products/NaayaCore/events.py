from zope.interface import implementer
from .interfaces import ICSVImportEvent
from .interfaces import IZipImportEvent


@implementer(ICSVImportEvent)
class CSVImportEvent(object):
    """Event triggered after a naaya content object has been added
    """

    def __init__(self, context, ids):
        self.context = context
        self.ids = ids

@implementer(IZipImportEvent)
class ZipImportEvent(object):
    """Event triggered after a successful zip upload
    """


    def __init__(self, context, zip_contents):
        self.context = context
        self.zip_contents = zip_contents
