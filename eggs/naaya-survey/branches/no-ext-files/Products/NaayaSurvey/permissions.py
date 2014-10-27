from Products.Naaya.permissions import _register_permissions

PERMISSION_ADD_REPORT = 'Naaya - Add Naaya Survey Report'
PERMISSION_ADD_ATTACHMENT = 'Naaya - Add Naaya Survey Attachment'
PERMISSION_ADD_ANSWER = 'Naaya - Add Naaya Survey Answer'
PERMISSION_VIEW_ANSWERS = 'Naaya - View Naaya Survey Answers'
PERMISSION_EDIT_ANSWERS = 'Naaya - Edit Naaya Survey Answers'
PERMISSION_VIEW_REPORTS = 'Naaya - View Naaya Survey Reports'
PERMISSION_ADD_MEGASURVEY = 'Naaya - Add Naaya Mega Survey'

permission_data = {
    PERMISSION_ADD_REPORT: {
        'title': 'Submit Survey Report objects',
        'description': """
            Create new survey reports.
        """,
    },
    PERMISSION_ADD_ATTACHMENT: {
        'title': 'Submit Survey Attachments',
        'description': """
            Attach files.
        """,
    },
    PERMISSION_ADD_ANSWER: {
        'title': 'Submit Survey Answer objects',
        'description': """
            Answer the survey.
        """,
    },
    PERMISSION_VIEW_ANSWERS: {
        'title': 'View survey answers',
        'description': """
        """,
    },
    PERMISSION_EDIT_ANSWERS: {
        'title': 'Edit survey answers',
        'description': """
        """,
    },
    PERMISSION_VIEW_REPORTS: {
        'title': 'View survey reports',
        'description': """
        """,
    },
    PERMISSION_ADD_MEGASURVEY: {
        'title': 'Submit Survey objects',
        'description': """
            Create new surveys.
        """,
    },
}

def register_permissions():
    _register_permissions(permission_data)
