from zope.interface import Interface, Attribute

from naaya.core.interfaces import INyObject

class INyContentObject(INyObject):
    """ An instance of a Naaya content type """
    pass

class INyContentObjectAddEvent(Interface):
    """ Naaya content object has been created """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who made the changes")
    schema_raw_data = Attribute("Schema arguments used to create the object")

class INyContentObjectEditEvent(Interface):
    """ Naaya content object has been edited """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who made the changes")

class INyContentObjectApproveEvent(Interface):
    """ Naaya content object has been approved """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who made the changes")

class INyContentObjectUnapproveEvent(Interface):
    """ Naaya content object has been unapproved """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who made the changes")

class INyContentObjectMovedEvent(Interface):
    """
    Naaya content object has been moved/renamed

    This event is more specific than Zope's ObjectMovedEvent: it only
    fires when an object is actually moved (not added or deleted), and
    it contains the object's path relative to the site root.
    """

    context = Attribute("INyContentObject instance")
    zope_event = Attribute("original ObjectMovedEvent instance")
    old_site_path = Attribute("object's path in site, before the move")
    new_site_path = Attribute("object's path in site, after the move")

class INyRdfView(Interface):
    """ Render an RDF document representing a given object """

class INyContentObjectExport(Interface):
    """ Export Ny Content object """

class INyContentObjectViewEvent(Interface):
    """ Naaya content object has been opened """

    context = Attribute("INyContentObject instance")
    user_id = Attribute("user_id of logged in user that performed access")

class INyContentObjectDownloadEvent(Interface):
    """ Naaya content object has been downloaded """

    context = Attribute("INyContentObject instance")
    user_id = Attribute("user_id of logged in user that performed access")
