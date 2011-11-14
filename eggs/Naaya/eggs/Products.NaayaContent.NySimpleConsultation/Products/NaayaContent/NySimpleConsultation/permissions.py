from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_SIMPLE_CONSULTATION = 'Naaya - Add Naaya Simple Consultation objects'
PERMISSION_REVIEW_SIMPLECONSULTATION = 'Naaya - Review Simple Consultation'
PERMISSION_MANAGE_SIMPLECONSULTATION = 'Naaya - Manage Simple Consultation'

permission_data = {
    PERMISSION_ADD_SIMPLE_CONSULTATION: {
        'title': 'Submit Simple Consultation objects',
        'description': """
            Create new simple consultation.
        """,
    },
    PERMISSION_REVIEW_SIMPLECONSULTATION: {
        'title': 'Review Simple Consultation objects',
        'description': """
            Submit comments.
        """,
    },
    PERMISSION_MANAGE_SIMPLECONSULTATION: {
        'title': 'Administer Simple Consultation objects',
        'description': """
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
