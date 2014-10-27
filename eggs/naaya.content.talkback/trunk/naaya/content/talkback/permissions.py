from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_TALKBACK_CONSULTATION = 'Naaya - Add Naaya TalkBack Consultation objects'
PERMISSION_REVIEW_TALKBACKCONSULTATION = 'Naaya - Review TalkBack Consultation'
PERMISSION_REVIEW_TALKBACKCONSULTATION_AFTER_DEADLINE = \
    'Naaya - Review TalkBack after deadline'
PERMISSION_MANAGE_TALKBACKCONSULTATION = 'Naaya - Manage TalkBack Consultation'
PERMISSION_INVITE_TO_TALKBACKCONSULTATION = 'Naaya - Invite to TalkBack Consultation'

permission_data = {
    PERMISSION_ADD_TALKBACK_CONSULTATION: {
        'title': 'Submit Talkback Consultation objects',
        'description': """
            Create new talkback consultations.
        """,
    },
    PERMISSION_REVIEW_TALKBACKCONSULTATION: {
        'title': 'TalkBack Consultation - submit review',
        'description': """
        """,
    },
    PERMISSION_REVIEW_TALKBACKCONSULTATION_AFTER_DEADLINE: {
        'title': 'TalkBack Consultation - submit review after deadline',
        'description': """
        """,
    },
    PERMISSION_INVITE_TO_TALKBACKCONSULTATION: {
        'title': 'TalkBack Consultation - invite participants',
        'description': """
            Invite people with no user on this portal
            to comment on TalkBack Consultations
        """,
    },
    PERMISSION_MANAGE_TALKBACKCONSULTATION: {
        'title': 'TalkBack Consultation - manage',
        'description': """
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
