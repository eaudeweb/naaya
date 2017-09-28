from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_ORGANISATION = 'Naaya - Add Naaya Organisation objects'

permission_data = {
    PERMISSION_ADD_ORGANISATION: {
        'title': 'Submit Organisation objects',
        'description': """
            Create new organisation objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
