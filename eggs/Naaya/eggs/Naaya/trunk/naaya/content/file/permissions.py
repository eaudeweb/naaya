from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_FILE = 'Naaya - Add Naaya File objects'

permission_data = {
    PERMISSION_ADD_FILE: {
        'title': 'Submit File objects',
        'description': """
            Create new files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
