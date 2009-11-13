from zope.interface import Interface, Attribute

from naaya.content.base.interfaces import INyContentObject

class INyContainer(Interface):
    """ Interface for NyContainer"""
    pass

class INyItem(Interface):
    """ Interface for NyItem"""
    pass

class INyFSFile(Interface):
    """ Interface for NyFSFile """
    pass
