from zope import interface

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

