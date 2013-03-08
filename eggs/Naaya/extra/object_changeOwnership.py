""" Change ownership for a specific object """

def change_ownership_for_object(username):
    """ Example of changing ownsership for a specific object """

    path_to_my_object = "/eea-2012-cc-iva-report-authors/library/"
                        "mihai-tabara-folder/survey-test")
    myobject = app.unrestrictedTraverse(path_to_my_object)
    acl_users = myobject.getSite().getAuthenticationTool()
    new_owner = acl_users.getUser(username)
    myobject.changeOwnership(user=new_owner)

