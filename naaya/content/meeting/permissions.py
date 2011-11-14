from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_MEETING = 'Naaya - Add Naaya Meeting objects'
PERMISSION_PARTICIPATE_IN_MEETING = 'Naaya - Meeting - Participate in the meeting'
PERMISSION_ADMIN_MEETING = 'Naaya - Meeting - Administrate the meeting'

permission_data = {
    PERMISSION_ADD_MEETING: {
        'title': 'Submit meetings',
        'description': """
            Create new meetings.
        """,
    },
    PERMISSION_PARTICIPATE_IN_MEETING: {
        'title': 'Participate to the meeting',
        'description': """
            View meeting folder contents and participants.
        """,
    },
    PERMISSION_ADMIN_MEETING: {
        'title': 'Administer the meeting',
        'description': """
            Send emails to participants, approve/reject meeting subscriptions.
        """,
    }
}

def register_permissions():
    _register_permissions(permission_data)
