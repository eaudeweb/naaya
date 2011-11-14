from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_EVENT = 'Naaya - Add Naaya Event objects'

permission_data = {
    PERMISSION_ADD_EVENT: {
        'title': 'Submit Event objects',
        'description': """
            Create new events.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
