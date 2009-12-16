from zope.interface import implements
from interfaces import INyAddLocalRoleEvent
from interfaces import INySetLocalRoleEvent
from interfaces import INyDelLocalRoleEvent

class NyAddLocalRoleEvent(object):
    """ Local role has been added """
    implements(INyAddLocalRoleEvent)

    def __init__(self, context, name, roles):
        super(NyAddLocalRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

class NySetLocalRoleEvent(object):
    """ Local role has been set """
    implements(INySetLocalRoleEvent)

    def __init__(self, context, name, roles):
        super(NySetLocalRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

class NyDelLocalRoleEvent(object):
    """ Local roles have been deleted """
    implements(INyDelLocalRoleEvent)

    def __init__(self, context, names):
        super(NyDelLocalRoleEvent, self).__init__()
        self.context, self.names = context, names

