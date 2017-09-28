from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_EXTENDED_FILE = 'Naaya - Add Naaya Extended File objects'

permission_data = {
    PERMISSION_ADD_EXTENDED_FILE: {
        'title': 'Submit Extended File objects',
        'description': """
            Create new extended file objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
