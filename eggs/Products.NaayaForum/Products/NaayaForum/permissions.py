from Products.Naaya.permissions import _register_permissions

from constants import (PERMISSION_ADD_FORUM,
                        PERMISSION_MODIFY_FORUMTOPIC,
                        PERMISSION_ADD_FORUMMESSAGE,
                        PERMISSION_MODIFY_FORUMMESSAGE,
                        )

permission_data = {
    PERMISSION_ADD_FORUM: {
        'title': 'Submit Forum objects',
        'description': """
            Create or edit forum objects.
        """,
    },
    PERMISSION_MODIFY_FORUMTOPIC: {
        'title': 'Forum - add / edit / modify topics',
        'description': """
            Create, edit or delete forum topics.
        """,
    },
    PERMISSION_ADD_FORUMMESSAGE: {
        'title': 'Forum - submit messages',
        'description': """
            Add new messages in forum topics or post replies to messages.
        """,
    },
    PERMISSION_MODIFY_FORUMMESSAGE: {
        'title': 'Forum - edit messages',
        'description': """
            Edit or delete forum messages or add/delete attachements to messages.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
