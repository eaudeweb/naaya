from zope.interface import Interface, Attribute

class INyContentObjectAddedEvent(Interface):
    """An event triggered when a naaya content object is added.
    """

    context = Attribute("The added content object")
    schema = Attribute("Schema arguments used to create the object")
