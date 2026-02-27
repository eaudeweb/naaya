from zope.interface import implementer

from Products.NaayaCore.AuthenticationTool.interfaces import IRoleAssignmentEvent

@implementer(IRoleAssignmentEvent)
class RoleAssignmentEvent(object):
    """ Event containing info about a role assignment/unassignment """

    def __init__(self, context, manager_id, user_id, assigned, unassigned,
            is_group=False, send_mail=False):
        self.context = context
        self.manager_id = manager_id
        self.user_id = user_id
        self.is_group = is_group
        self.assigned = assigned
        self.unassigned = unassigned
        self.send_mail = send_mail

