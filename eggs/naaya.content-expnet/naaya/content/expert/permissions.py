from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_EXPERT = 'Naaya - Add Naaya Expert objects'

permission_data = {
    PERMISSION_ADD_EXPERT: {
        'title': 'Submit Expert objects',
        'description': """
            Create new expert objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
