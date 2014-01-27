from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_MEDIA_FILE = 'Naaya - Add Naaya Media File objects'

permission_data = {
    PERMISSION_ADD_MEDIA_FILE: {
        'title': 'Submit Media File objects',
        'description': """
            Create new media files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
