from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_BESTPRACTICE = 'Naaya - Add Naaya Best Practice objects'

permission_data = {
    PERMISSION_ADD_BESTPRACTICE: {
        'title': 'Submit Best Practice objects',
        'description': """
            Create new best practice files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
