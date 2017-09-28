from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_CONTACT = 'Naaya - Add Naaya Contact objects'

permission_data = {
    PERMISSION_ADD_CONTACT: {
        'title': 'Submit Contact objects',
        'description': """
            Create new contacts.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
