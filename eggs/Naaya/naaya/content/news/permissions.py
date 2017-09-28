from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_NEWS = 'Naaya - Add Naaya News objects'

permission_data = {
    PERMISSION_ADD_NEWS: {
        'title': 'Submit News objects',
        'description': """
            Create new news objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
