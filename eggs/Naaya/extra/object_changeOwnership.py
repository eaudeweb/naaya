""" Change ownership for a specific object """

def change_ownership_for_object(ob, username):
    """ Example of changing ownsership for a specific object """
    app = ob.unrestrictedTraverse("/")
    user = app.acl_users.getUser(username)
    new_owner = user.__of__(app.acl_users)
    ob.changeOwnership(user=new_owner)

