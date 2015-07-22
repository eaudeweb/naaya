"""
This module contains global constants.
"""


import Globals


NAAYABASE_PRODUCT_NAME = 'NaayaBase'
NAAYABASE_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADMINISTRATE = 'Naaya - Access administrative area'
PERMISSION_PUBLISH_OBJECTS = 'Naaya - Publish content'
PERMISSION_EDIT_OBJECTS = 'Naaya - Edit content'
PERMISSION_COPY_OBJECTS = 'Naaya - Copy content'
PERMISSION_DELETE_OBJECTS = 'Naaya - Delete content'
PERMISSION_VALIDATE_OBJECTS = 'Naaya - Validate content'
PERMISSION_COMMENTS_ADD = 'Naaya - Add comments for content'
PERMISSION_COMMENTS_MANAGE = 'Naaya - Manage comments for content'
PERMISSION_PUBLISH_DIRECT = 'Naaya - Publish direct'
PERMISSION_SKIP_CAPTCHA = 'Naaya - Skip Captcha'
PERMISSION_BULK_DOWNLOAD = 'Naaya - Bulk download'
PERMISSION_SKIP_APPROVAL = 'Naaya - Skip approval'
PERMISSION_ZIP_EXPORT = 'Naaya - Zip export'
PERMISSION_CREATE_USER = 'Naaya - Create user'
PERMISSION_REQUEST_WEBEX = 'Naaya - Request Webex'

# Exceptions
EXCEPTION_NOTIMPLEMENTED = 'NotImplemented'
EXCEPTION_NOTACCESIBLE = 'NotAccesible'
EXCEPTION_NOTAUTHORIZED = 'Unauthorized'
EXCEPTION_NOTAUTHORIZED_MSG = 'You are not authorized to access this resource'
EXCEPTION_NOVERSION = 'NoVersionStarted'
EXCEPTION_NOVERSION_MSG = 'The object hasn\'t been locked out'
EXCEPTION_STARTEDVERSION = 'VersionStarted'
EXCEPTION_STARTEDVERSION_MSG = 'The object is locked out'
EXCEPTION_PARSINGFILE = 'Error parsing file %s: %s'
EXCEPTION_CONFLICTERROR = 'ConflictError'
PRETTY_EXCEPTION_MSG = {
    EXCEPTION_CONFLICTERROR:
        ('Another user is modifying concurrent data that conflicts with your action.'
         ' He was still saving data while your request was retried three times.<br />'
         'Please reload the page, resubmit your form (if any) or go back and try again.'),
}

# Others
MESSAGE_SAVEDCHANGES = 'Saved changes. (${date})'
MESSAGE_ERROROCCURRED = 'An error occurred while trying to save changes.'
MESSAGE_NOTFROMEMAIL = 'The Sender email was not provided. Changes NOT saved (%s)'
ERROR_NOTHING_SELECTED = 'Nothing was selected.'
