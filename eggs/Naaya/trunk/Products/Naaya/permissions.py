from textwrap import dedent
from constants import PERMISSION_ADD_FOLDER
from Products.NaayaBase.constants import (PERMISSION_SKIP_APPROVAL,
                                          PERMISSION_ZIP_EXPORT)


permission_data = {
    'Naaya - Add comments for content': {
        'title': "Submit comments",
        'description': """
            Submit comments for Naaya content items. The comment button
            appears at the bottom of an object's index page.
        """,
    },
    'Naaya - Copy content': {
        'title': "Copy objects",
        'description': """
            Copy content items from one folder to another.
        """,
    },
    'Naaya - Delete content': {
        'title': "Delete objects",
        'description': """
            Remove content from a folder. If the "Owner" role has
            this permission, then contributors will be able to remove
            their own content.
        """,
    },
    'Naaya - Edit content': {
        'title': "Edit objects",
        'description': """
            Edit and translate the content items.
        """,
    },
    'Naaya - Manage comments for content': {
        'title': "Manage comments",
        'description': """
            Edit and remove comments submitted for content items.
        """,
    },
    'Naaya - Publish content': {
        'title': "Administration",
        'description': """
            Change the portal's configurations, manage all content,
            manage users and roles and all the settings
            from the Administration area
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
    PERMISSION_ZIP_EXPORT: {
        'title': "Export folder as Zip",
        'description': """
            Export contents of folder as Zip file. Also applies to Naaya Photo
            Folder.
        """,
    },
    'Naaya - Validate content': {
        'title': "Validate objects",
        'description': """
            Validate content items.
        """,
    },
    PERMISSION_ADD_FOLDER: {
        'title': "Submit Folder objects",
        'description': """
            Create new folder objects.
        """,
    },
    PERMISSION_SKIP_APPROVAL: {
        'title': "Skip the approval process",
        'description': """
            Newly created objects will be automatically approved
            without going through the review/approval workflow.
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

NAAYA_KNOWN_PERMISSIONS = {}
def register_naaya_permission(zope_perm, title, description=""):
    """
    Register a permission so that administrators can assign it to roles.

    """
    NAAYA_KNOWN_PERMISSIONS[zope_perm] = {
        'title': title,
        'description': description,
        'zope_permission': zope_perm,
    }

def _register_permissions(permission_data):
    for zope_perm, info in permission_data.iteritems():
        register_naaya_permission(zope_perm,
                                  info['title'],
                                  dedent(info['description']))

def register_permissions():
    _register_permissions(permission_data)
