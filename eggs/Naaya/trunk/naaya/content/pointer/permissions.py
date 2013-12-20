from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_POINTER = 'Naaya - Add Naaya Pointer objects'

permission_data = {
    PERMISSION_ADD_POINTER: {
        'title': 'Submit Pointer objects',
        'description': """
            Create new pointer objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
