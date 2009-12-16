
def handle_add_local_role(event):
    event.context.addLocalRolesInfo(event.name, event.roles)

def handle_set_local_role(event):
    event.context.setLocalRolesInfo(event.name, event.roles)

def handle_del_local_role(event):
    event.context.delLocalRolesInfo(event.names)

