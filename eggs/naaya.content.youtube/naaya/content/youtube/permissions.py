from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_YOUTUBE = 'Naaya - Add Naaya Youtube objects'

permission_data = {
    PERMISSION_ADD_YOUTUBE: {
        'title': 'Submit Youtube objects',
        'description': """
            Create new Youtube embeded videos.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
