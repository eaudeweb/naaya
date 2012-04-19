from zope.interface import Interface
from naaya.content.base.interfaces import INyContentObjectExport

class INyDocument(Interface):
    """ Naaya HTML Document content type """

class INyContentDocumentExport(INyContentObjectExport):
    """ Export HTML Document """