from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_PHOTOGALLERY = 'Naaya - Add Naaya Photo Gallery'
PERMISSION_ADD_PHOTOFOLDER = 'Naaya - Add Naaya Photo Folder'
PERMISSION_ADD_PHOTO = 'Naaya - Add Naaya Photo'

permission_data = {
    PERMISSION_ADD_PHOTOGALLERY: {
        'title': 'Submit Photo Gallery objects',
        'description': """
            Create new photo galleries.
        """,
    },
    PERMISSION_ADD_PHOTOFOLDER: {
        'title': 'Submit Photo Folder objects',
        'description': """
            Create new photo folders.
        """,
    },
    PERMISSION_ADD_PHOTO: {
        'title': 'Submit Photo objects',
        'description': """
            Create new photos.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
