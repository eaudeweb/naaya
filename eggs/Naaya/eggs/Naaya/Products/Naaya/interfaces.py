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

class INyAddLocalRoleEvent(Interface):
    """ Local role has been added """

    context = Attribute("Site or folder the roles are added for")
    name = Attribute("UID of the user the roles are added for")
    roles = Attribute("The list of roles")

class INySetLocalRoleEvent(Interface):
    """ Local role has been set """

    context = Attribute("Site or folder the roles are set for")
    name = Attribute("UID of the user the roles are set for")
    roles = Attribute("The list of roles")

class INyDelLocalRoleEvent(Interface):
    """ Local roles have been deleted """

    context = Attribute("Site or folder the roles are deleted for")
    name = Attribute("UID of the user the roles are deleted for")

