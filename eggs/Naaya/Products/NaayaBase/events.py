from zope.interface import implementer

from .interfaces import INyAddLocalRoleEvent, INySetLocalRoleEvent
from .interfaces import INyDelLocalRoleEvent, INyAddUserRoleEvent
from .interfaces import INySetUserRoleEvent, INyDelUserRoleEvent
from .interfaces import INyAddGroupRoleEvent, INyRemoveGroupRoleEvent
from .interfaces import INyCommentAddEvent

@implementer(INyAddLocalRoleEvent)
class NyAddLocalRoleEvent(object):
    """ Local role will be added """

    def __init__(self, context, name, roles):
        super(NyAddLocalRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

@implementer(INySetLocalRoleEvent)
class NySetLocalRoleEvent(object):
    """ Local role will be set """

    def __init__(self, context, name, roles):
        super(NySetLocalRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

@implementer(INyDelLocalRoleEvent)
class NyDelLocalRoleEvent(object):
    """ Local roles will be deleted """

    def __init__(self, context, names):
        super(NyDelLocalRoleEvent, self).__init__()
        self.context, self.names = context, names


@implementer(INyAddUserRoleEvent)
class NyAddUserRoleEvent(object):
    """ User role will be added """

    def __init__(self, context, name, roles):
        super(NyAddUserRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

@implementer(INySetUserRoleEvent)
class NySetUserRoleEvent(object):
    """ User role will be set """

    def __init__(self, context, name, roles):
        super(NySetUserRoleEvent, self).__init__()
        self.context, self.name, self.roles = context, name, roles

@implementer(INyDelUserRoleEvent)
class NyDelUserRoleEvent(object):
    """ User roles will be deleted """

    def __init__(self, context, names):
        super(NyDelUserRoleEvent, self).__init__()
        self.context, self.names = context, names

@implementer(INyAddGroupRoleEvent)
class NyAddGroupRoleEvent(object):
    """ Group roles will be added """

    def __init__(self, context, group, roles):
        super(NyAddGroupRoleEvent, self).__init__()
        self.context, self.group, self.roles = context, group, roles

@implementer(INyRemoveGroupRoleEvent)
class NyRemoveGroupRoleEvent(object):
    """ Group roles will be removed """

    def __init__(self, context, group, roles):
        super(NyRemoveGroupRoleEvent, self).__init__()
        self.context, self.group, self.roles = context, group, roles

@implementer(INyCommentAddEvent)
class NyCommentAddEvent(object):
    """ A comment was added """

    def __init__(self, context, contributor, parent_ob):
        self.parent_ob = parent_ob
        self.context = context
        self.contributor = contributor
