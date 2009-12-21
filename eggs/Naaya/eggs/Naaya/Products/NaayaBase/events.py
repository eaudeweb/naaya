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

#Python

#Zope
from zope.interface import implements

#Products
from interfaces import INyAddLocalRoleEvent, INySetLocalRoleEvent, INyDelLocalRoleEvent
from interfaces import INyAddUserRoleEvent, INySetUserRoleEvent, INyDelUserRoleEvent

class NyAddLocalRoleEvent(object):
    """ Local role will be added """
    implements(INyAddLocalRoleEvent)

    def __init__(self, context, name, roles):
        super(NyAddLocalRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

class NySetLocalRoleEvent(object):
    """ Local role will be set """
    implements(INySetLocalRoleEvent)

    def __init__(self, context, name, roles):
        super(NySetLocalRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

class NyDelLocalRoleEvent(object):
    """ Local roles will be deleted """
    implements(INyDelLocalRoleEvent)

    def __init__(self, context, names):
        super(NyDelLocalRoleEvent, self).__init__()
        self.context, self.names = context, names


class NyAddUserRoleEvent(object):
    """ User role will be added """
    implements(INyAddUserRoleEvent)

    def __init__(self, context, name, roles):
        super(NyAddUserRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

class NySetUserRoleEvent(object):
    """ User role will be set """
    implements(INySetUserRoleEvent)

    def __init__(self, context, name, roles):
        super(NySetUserRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

class NyDelUserRoleEvent(object):
    """ User roles will be deleted """
    implements(INyDelUserRoleEvent)

    def __init__(self, context, names):
        super(NyDelUserRoleEvent, self).__init__()
        self.context, self.names = context, names

