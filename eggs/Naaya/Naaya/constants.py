METATYPE_NOTIFICATION_LIST = 'Naaya Folder Notification List'
NOTIFICATION_LIST_DEFAULT_ID = 'notification_list'
PERMISSION_MANAGE_NOTIFICATION_LIST = 'Naaya - Manage Notification List'

NOTIFICATION_LIST_MAIL_BODY_TEMPLATE = """\
This is an automatically generated message to inform you that 
the item '@@ITEMTITLEORID@@' is uploaded to the library @@CONTAINERPATH@@.

Uploaded by @@USERNAME@@(@@USEREMAIL@@) on @@UPLOADTIME@@.
"""

NOTIFICATION_LIST_MAIL_SUBJECT_TEMPLATE = "Upload notification: %s"
