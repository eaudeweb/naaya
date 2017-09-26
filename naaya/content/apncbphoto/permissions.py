from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_APNCBPHOTO = 'Naaya - Add Naaya APNCB Photo archives'

permission_data = {
    PERMISSION_ADD_APNCBPHOTO: {
        'title': 'Submit APNCB Photo archives',
        'description': """
            Create new Photo archive connection.
        """,
    },
}


def register_permissions():
    _register_permissions(permission_data)
