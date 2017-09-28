from zope.interface import Interface, Attribute

class INyContainer(Interface):
    """ Interface for NyContainer"""
    pass

class INyItem(Interface):
    """ Interface for NyItem"""
    pass

class INyFSFile(Interface):
    """ Interface for NyFSFile """
    pass

class INyCommentable(Interface):
    """ Interface for NyCommentable """
    pass

class INyCommentAddEvent(Interface):
    """ A comment was added """

    context = Attribute("INyContentObject instance")
    contributor = Attribute("user_id of user who added the comment")

class INyComment(Interface):
    """ Interface for NyComment """
    pass

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
    names = Attribute("List of UIDs the roles are deleted for")


class INyAddUserRoleEvent(Interface):
    """ User  role has been added """

    context = Attribute("Site or folder the roles are added for")
    name = Attribute("UID of the user the roles are added for")
    roles = Attribute("The list of roles")

class INySetUserRoleEvent(Interface):
    """ User role has been set """

    context = Attribute("Site or folder the roles are set for")
    name = Attribute("UID of the user the roles are set for")
    roles = Attribute("The list of roles")

class INyDelUserRoleEvent(Interface):
    """ User roles have been deleted """

    context = Attribute("Site or folder the roles are deleted for")
    names = Attribute("List of UIDs the roles are deleted for")

class INyAddGroupRoleEvent(Interface):
    """ LDAP group roles have been added """

    context = Attribute("Site or folder the roles are added for")
    group = Attribute("Group the roles are set for")
    roles = Attribute("The list of roles")

class INyRemoveGroupRoleEvent(Interface):
    """ LDAP group roles have been removed """

    context = Attribute("Site or folder the roles are removed for")
    group = Attribute("Group the roles are removed for")
    roles = Attribute("The list of roles")

class IRoleLogger(Interface):
    """ Log local role assignments and revocations """

class INyFeedHarvester(Interface):
    """ Utility that can fetch a remote feed and parse it """

    def harvest_feed(self, feed):
        """
        Perform harvesting operation. `feed` is a NyFeed object, useful e.g.
        to find out the URL.

        See what the default parser in `NyFeed.harvest_feed` does and try to
        emulate its behaviour :)
        """
