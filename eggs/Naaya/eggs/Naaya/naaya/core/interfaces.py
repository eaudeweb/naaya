from zope.interface import Interface

class INyObject(Interface):
    """ A generic Naaya object that supports some basic methods """

    def getSite():
        """ Returns the containing NySite instance """
