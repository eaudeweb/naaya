from zope.interface import Interface, Attribute

from naaya.core.interfaces import INyObject

class INyContentObject(INyObject):
    """ An instance of a Naaya content type """

    def version_status():
        """ returns html that discribes the versioning status """


class INyContentObjectAddEvent(Interface):
    """ Naaya content object has been created """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who made the changes")
    schema_raw_data = Attribute("Schema arguments used to create the object")


class INyContentObjectEditEvent(Interface):
    """ Naaya content object has been edited """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who made the changes")
