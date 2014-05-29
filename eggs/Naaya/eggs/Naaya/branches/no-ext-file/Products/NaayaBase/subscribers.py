from interfaces import IRoleLogger

def handle_add_local_role(event):
    IRoleLogger(event.context).addLocalRolesInfo(event.name, event.roles)

def handle_set_local_role(event):
    IRoleLogger(event.context).setLocalRolesInfo(event.name, event.roles)

def handle_del_local_role(event):
    IRoleLogger(event.context).delLocalRolesInfo(event.names)

def handle_add_user_role(event):
    IRoleLogger(event.context).addUserRolesInfo(event.name, event.roles)

def handle_set_user_role(event):
    IRoleLogger(event.context).setUserRolesInfo(event.name, event.roles)

def handle_del_user_role(event):
    IRoleLogger(event.context).delUserRolesInfo(event.names)

def handle_add_group_roles(event):
    IRoleLogger(event.context).addLDAPGroupRolesInfo(event.group, event.roles)

def handle_remove_group_roles(event):
    IRoleLogger(event.context).removeLDAPGroupRolesInfo(event.group,
                                                        event.roles)
