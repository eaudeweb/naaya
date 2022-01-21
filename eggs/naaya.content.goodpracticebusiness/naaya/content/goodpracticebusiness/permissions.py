from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_GOODPRACTICEBUSINESS = 'Naaya - Add Naaya Good Practice Business objects'

permission_data = {
    PERMISSION_ADD_GOODPRACTICEBUSINESS: {
        'title': 'Submit Good Practice Business objects',
        'description': """
            Create new good practice business files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
