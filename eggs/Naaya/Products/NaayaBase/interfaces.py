from zope.interface import Interface, Attribute

class INyContainer(Interface):
    """ Interface for NyContainer"""
    pass

class INyItem(Interface):
    """ Interface for NyItem"""
    pass

class INyFSFile(Interface):
    """ Interface for NyFSFile """
    pass

class INyContentType(Interface):
    """ """
    def version_status():
        """ returns html that discribes the versioning status """

