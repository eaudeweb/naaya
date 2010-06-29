from zope.interface import Interface

# import for compatibility
from naaya.core.interfaces import IHeartbeat

class INySite(Interface):
    """ Interface for NySite"""
    pass

class INyFolder(Interface):
    """ Interface for NyFolder"""
    pass

class IObjectView(Interface):
    """  """
    def version_status():
        """ returns tuple (versionable, editable) """
