from OFS.interfaces import IItem

class INyObject(IItem):
    """ A generic Naaya object that supports some basic methods """

    def getSite():
        """ Returns the containing NySite instance """
