from zope.interface import Interface, Attribute

class INySite(Interface):
    """ Interface for NySite"""
    pass

class INyFolder(Interface):
    """ Interface for NyFolder"""
    pass

class IHeartbeat(Interface):
    """ Interface for Heartbeat """
    when = Attribute('when')

class IObjectView(Interface):
    """ """
    def version_status_html():
        """ returns html that discribes the versioning status """

