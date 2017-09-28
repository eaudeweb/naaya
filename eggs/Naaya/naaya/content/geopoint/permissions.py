from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_GEOPOINT = 'Naaya - Add Naaya GeoPoint objects'

permission_data = {
    PERMISSION_ADD_GEOPOINT: {
        'title': 'Submit GeoPoint objects',
        'description': """
            Create new geopoint objects.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
