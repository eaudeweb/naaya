from zope.interface import implements

from interfaces import INyAddLocalRoleEvent, INySetLocalRoleEvent
from interfaces import INyDelLocalRoleEvent, INyAddUserRoleEvent
from interfaces import INySetUserRoleEvent, INyDelUserRoleEvent
from interfaces import INyAddGroupRoleEvent, INyRemoveGroupRoleEvent
from interfaces import INyCommentAddEvent

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

class NyAddGroupRoleEvent(object):
    """ Group roles will be added """
    implements(INyAddGroupRoleEvent)

    def __init__(self, context, group, roles):
        super(NyAddGroupRoleEvent, self).__init__()
        self.context, self.group, self.roles = context, group, roles

class NyRemoveGroupRoleEvent(object):
    """ Group roles will be removed """
    implements(INyRemoveGroupRoleEvent)

    def __init__(self, context, group, roles):
        super(NyRemoveGroupRoleEvent, self).__init__()
        self.context, self.group, self.roles = context, group, roles

class NyCommentAddEvent(object):
    """ A comment was added """
    implements(INyCommentAddEvent)

    def __init__(self, context, contributor, parent_ob):
        self.parent_ob = parent_ob
        self.context = context
        self.contributor = contributor
