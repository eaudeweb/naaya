from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_LOCALIZED_BFILE = 'Naaya - Add Naaya Localized Blob File'

permission_data = {
    PERMISSION_ADD_LOCALIZED_BFILE: {
        'title': 'Submit Localized Blob File objects',
        'description': """
            Create new localized blob files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
