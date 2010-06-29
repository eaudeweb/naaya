from zope.interface import Interface, Attribute

from OFS.interfaces import IItem

class INyObject(IItem):
    """ A generic Naaya object that supports some basic methods """

    def getSite():
        """ Returns the containing NySite instance """

class INyObjectContainer(Interface):
    """
    An object that may contain other Naaya objects. Useful when generating
    sitemaps or rebuilding the catalog.
    """

class IHeartbeat(Interface):
    """ Interface for Heartbeat event """
    when = Attribute('when')
