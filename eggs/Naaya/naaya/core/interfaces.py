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

    def objectValues():
        """ Get a list of contained objects. """

class IHeartbeat(Interface):
    """ Interface for Heartbeat event """
    when = Attribute('when')


class IFilesystemBundleFactory(Interface):
    """ Create a filesystem bundle for a given site. """
    def create_bundle():
        """ Write the new bundle in the filesystem and return it. """


class IRstkMethod(Interface):
    """ Method accessible on a RestrictedToolkit object. """
    def __call__(*args, **kwargs):
        """ Call the method. """


class IExternalApplicationFrame(Interface):
    """
    Marker interface to define a "frame" service, to be used by an
    external application.
    """
