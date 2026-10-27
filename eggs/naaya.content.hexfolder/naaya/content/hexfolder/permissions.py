from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_HEXFOLDER = 'Naaya - Add Naaya Hex Folder objects'

permission_data = {
    PERMISSION_ADD_HEXFOLDER: {
        'title': 'Submit Hexfolder objects',
        'description': """
            Create new folders with hex layout.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
