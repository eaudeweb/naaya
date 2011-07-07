from textwrap import dedent
from constants import PERMISSION_ADD_FOLDER
from Products.NaayaBase.constants import PERMISSION_SKIP_APPROVAL

permission_data = {
    'Naaya - Add comments for content': {
        'title': "Submit comments",
        'description': """
            Submit comments for Naaya content objects. The comment button
            appears at the bottom of an object's index page.
        """,
    },
    'Naaya - Copy content': {
        'title': "Copy objects",
        'description': """
            Copy content objects from one folder to another.
        """,
    },
    'Naaya - Delete content': {
        'title': "Delete objects",
        'description': """
            Remove content objects from a folder. If the "Owner" role has this
            permission, then contributors will be able to remove their own
            content.
        """,
    },
    'Naaya - Edit content': {
        'title': "Edit objects",
        'description': """
            Edit any content object.
        """,
    },
    'Naaya - Manage comments for content': {
        'title': "Manage comments",
        'description': """
            Edit and remove comments submitted for content objects.
        """,
    },
    'Naaya - Publish content': {
        'title': "Administration",
        'description': """
            Change a portal's configuration, add/remove users, grant and
            revoke roles, etc.
        """,
    },
    'Naaya - Skip Captcha': {
        'title': "Skip captcha verification",
        'description': """
            No captcha verification will be performed when submitting content
            objects, survey answers, etc.
        """,
    },
    'Naaya - Translate pages': {
        'title': "Translate messages",
        'description': """
            Translate portal messages into other languages.
        """,
    },
    'Naaya - Zip export': {
        'title': "Export folder as Zip",
        'description': """
            Export contents of folder as Zip file.
        """,
    },
    'Naaya - Validate content': {
        'title': "Validate objects",
        'description': """
            Approve/unapprove content objects.
        """,
    },
    PERMISSION_ADD_FOLDER: {
        'title': "Submit Folder objects",
        'description': """
            Create new content objects of type NyFolder.
        """,
    },
    PERMISSION_SKIP_APPROVAL: {
        'title': "Skip the approval process",
        'description': """
            Newly created objects will be automatically approved without going
            through the validation workflow.
        """,
    },
    'View': {
        'title': "Access content",
        'description': """
            Access pages in the portal, without changing anything.
        """,
    },
    'Change permissions': {
        'title': "Change permissions",
        'description': """
            Change the permissions associated with a role.
        """,
    },
}

def register_default_permissions():
    from NySite import register_naaya_permission
    for zope_perm, info in permission_data.iteritems():
        register_naaya_permission(zope_perm,
                                  info['title'],
                                  dedent(info['description']))
