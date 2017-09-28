from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_STORY = 'Naaya - Add Naaya Story objects'

permission_data = {
    PERMISSION_ADD_STORY: {
        'title': 'Submit Story objects',
        'description': """
            Create new stories.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
