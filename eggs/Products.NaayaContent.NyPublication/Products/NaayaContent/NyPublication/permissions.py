from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_PUBLICATION = 'Naaya - Add Naaya Publication objects'

permission_data = {
    PERMISSION_ADD_PUBLICATION: {
        'title': 'Submit Publication objects',
        'description': """
            Create new publication objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
