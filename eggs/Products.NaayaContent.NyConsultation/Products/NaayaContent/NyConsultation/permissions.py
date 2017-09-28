from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_CONSULTATION = 'Naaya - Add Naaya Consultation objects'

permission_data = {
    PERMISSION_ADD_CONSULTATION: {
        'title': 'Submit Consultation objects',
        'description': """
            Create new consultations.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
