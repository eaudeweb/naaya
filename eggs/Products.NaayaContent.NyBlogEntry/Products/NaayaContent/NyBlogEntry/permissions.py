from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_BLOG_ENTRY = 'Naaya - Add Naaya Blog Entry objects'

permission_data = {
    PERMISSION_ADD_BLOG_ENTRY: {
        'title': 'Submit Blog Entry objects',
        'description': """
            Create new blog entries.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
