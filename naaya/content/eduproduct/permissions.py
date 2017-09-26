from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_EDU_PRODUCT = 'Naaya - Add Naaya Educational Product objects'

permission_data = {
    PERMISSION_ADD_EDU_PRODUCT: {
        'title': 'Submit Educational Product objects',
        'description': """
            Create new education product objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
