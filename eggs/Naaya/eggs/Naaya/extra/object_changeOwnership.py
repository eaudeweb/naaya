""" Change ownership for a specific object """

def change_ownership_for_object(ob, username):
    """ Example of changing ownsership for a specific object """

    acl_users = ob.getSite().getAuthenticationTool()
    new_owner = acl_users.getUser(username)
    ob.changeOwnership(user=new_owner)

