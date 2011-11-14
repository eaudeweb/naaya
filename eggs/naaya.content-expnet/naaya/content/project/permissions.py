from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_PROJECT = 'Naaya - Add Naaya Project objects'

permission_data = {
    PERMISSION_ADD_PROJECT: {
        'title': 'Submit Project objects',
        'description': """
            Create new project objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
