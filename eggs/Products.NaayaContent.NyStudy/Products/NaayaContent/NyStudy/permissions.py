from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_STUDY = 'Naaya - Add Naaya Study objects'

permission_data = {
    PERMISSION_ADD_STUDY: {
        'title': 'Submit Study objects',
        'description': """
            Create new study objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
