from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_BESTPRACTICEBUSINESS = 'Naaya - Add Naaya Best Practice Business objects'

permission_data = {
    PERMISSION_ADD_BESTPRACTICEBUSINESS: {
        'title': 'Submit Best Practice Business objects',
        'description': """
            Create new best practice business files.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
