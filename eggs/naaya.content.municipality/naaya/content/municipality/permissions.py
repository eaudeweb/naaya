from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_MUNICIPALITY = 'Naaya - Add Naaya Municipality objects'
PERMISSION_EDIT_MUNICIPALITY = 'Naaya - Edit Naaya Municipality objects'

permission_data = {
    PERMISSION_ADD_MUNICIPALITY: {
        'title': 'Submit Municipality objects',
        'description': """
            Create new municipality objects.
        """,
    },
    PERMISSION_EDIT_MUNICIPALITY: {
        'title': 'Edit Municipality objects',
        'description': """
            Edit municipality objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
