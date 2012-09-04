from zope.interface import implements

from Products.NaayaCore.AuthenticationTool.interfaces import IRoleAssignmentEvent

class RoleAssignmentEvent(object):
    """ Event containing info about a role assignment/unassignment """
    implements(IRoleAssignmentEvent)

    def __init__(self, context, manager_id, user_id, assigned, unassigned):
        self.context = context
        self.manager_id = manager_id
        self.user_id = user_id
        self.assigned = assigned
        self.unassigned = unassigned
