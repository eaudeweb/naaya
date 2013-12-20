from zope import interface

class IRoleAssignmentEvent(interface.Interface):
    """
    When you assign roles in a location, the previous ones are lost,
    that's why we are going to treat assignment and unassignment with the
    same type of event.

    """
    context = interface.Attribute("Location where roles were changed")
    manager_id = interface.Attribute("user_id of user who made the changes")
    user_id = interface.Attribute("user_id of user whose roles where changed")
    assigned = interface.Attribute("list containing assigned roles")
    unassigned = interface.Attribute("list containing unassigned roles")

class IAuthenticationToolPlugin(interface.Interface):
    """ An authentication tool plugin is a provider of user authentication
    methods.

    For example when connecting Naaya to LDAP there should be a plugin that
    acts as a gateway between the `AuthenticationTool` and the
    `Products.LDAPUserFolder`

    """

    def getUserFullName(self, p_username, acl_folder):
        """Return the full name of the given username from a specific
        acl_folder

        """

