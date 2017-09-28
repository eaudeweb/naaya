from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_CASE_STUDY = 'Naaya - Add Naaya Case Study objects'

permission_data = {
    PERMISSION_ADD_CASE_STUDY: {
        'title': 'Submit Case Study objects',
        'description': """
            Create new case study objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
