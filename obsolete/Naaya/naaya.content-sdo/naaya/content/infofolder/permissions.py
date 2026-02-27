from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_INFO = 'Naaya - Add Naaya Info'
PERMISSION_ADD_INFOFOLDER = 'Naaya - Add Naaya InfoFolder'
PERMISSION_EDIT_INFO = 'Naaya - Edit Naaya Info'

permission_data = {
    PERMISSION_ADD_INFO: {
        'title': 'Submit Info objects',
        'description': """
            Create new enterprise, network, tool and training objects.
        """,
    },
    PERMISSION_ADD_INFOFOLDER: {
        'title': 'Submit InfoFolder objects',
        'description': """
            Create new info folders.
        """,
    },
    PERMISSION_EDIT_INFO: {
        'title': 'Edit Info objects',
        'description': """
            Edit enterprise, network, tool and training objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
