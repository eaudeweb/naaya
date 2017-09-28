from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_URL = 'Naaya - Add Naaya URL objects'

permission_data = {
    PERMISSION_ADD_URL: {
        'title': 'Submit URL objects',
        'description': """
            Create new URL objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
