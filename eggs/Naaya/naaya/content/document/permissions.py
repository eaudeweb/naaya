from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_DOCUMENT = 'Naaya - Add Naaya Document objects'

permission_data = {
    PERMISSION_ADD_DOCUMENT: {
        'title': 'Submit Document objects',
        'description': """
            Create new documents.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)

