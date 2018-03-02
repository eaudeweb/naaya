from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_CERTIFICATE = 'Naaya - Add Naaya Certificate objects'

permission_data = {
    PERMISSION_ADD_CERTIFICATE: {
        'title': 'Submit Certificate objects',
        'description': """
            Create new certificate objects.
        """,
    },
}


def register_permissions():
    _register_permissions(permission_data)
