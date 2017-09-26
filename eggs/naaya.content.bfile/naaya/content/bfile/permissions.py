from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_BFILE = 'Naaya - Add Naaya Blob File objects'

permission_data = {
    PERMISSION_ADD_BFILE: {
        'title': 'Submit Blob File objects',
        'description': """
            Create new blob files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
