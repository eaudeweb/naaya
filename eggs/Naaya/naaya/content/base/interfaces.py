from zope.interface import Interface, Attribute

from naaya.core.interfaces import INyObject

class INyContentObject(INyObject):
    """ An instance of a Naaya content type """

    def version_status():
        """ returns html that discribes the versioning status """

class INyContentObjectAddedEvent(Interface):
    """An event triggered when a naaya content object is added.
    """

    context = Attribute("The added content object")
    schema = Attribute("Schema arguments used to create the object")
