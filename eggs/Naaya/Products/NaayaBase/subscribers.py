# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

def handle_add_local_role(event):
    event.context.addLocalRolesInfo(event.name, event.roles)

def handle_set_local_role(event):
    event.context.setLocalRolesInfo(event.name, event.roles)

def handle_del_local_role(event):
    event.context.delLocalRolesInfo(event.names)

def handle_add_user_role(event):
    event.context.addUserRolesInfo(event.name, event.roles)

def handle_set_user_role(event):
    event.context.setUserRolesInfo(event.name, event.roles)

def handle_del_user_role(event):
    event.context.delUserRolesInfo(event.names)

