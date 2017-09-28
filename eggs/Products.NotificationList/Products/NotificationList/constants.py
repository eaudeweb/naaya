METATYPE_NOTIFICATION_LIST = 'Naaya Folder Notification List'
NOTIFICATION_LIST_DEFAULT_ID = 'notification_list'
PERMISSION_MANAGE_NOTIFICATION_LIST = 'Naaya - Manage Notification List'

NOTIFICATION_LIST_MAIL_SUBJECT_TEMPLATE_UPLOAD = "Upload notification: %s"
NOTIFICATION_LIST_MAIL_BODY_TEMPLATE_UPLOAD = """\
This is an automatically generated message to inform you that 
the item "@@ITEM@@" is uploaded to @@GROUPTITLE@@:

@@ITEMURL@@

Uploaded by @@USERNAME@@(@@USEREMAIL@@) on @@UPLOADTIME@@.
"""

NOTIFICATION_LIST_MAIL_SUBJECT_TEMPLATE_FORUM_MESSAGE = "Forum message notification: %s"
NOTIFICATION_LIST_MAIL_BODY_TEMPLATE_FORUM_MESSAGE = """\
This is an automatically generated message to inform you that 
a new message has been posted to "@@GROUPTITLE@@":

@@ITEMURL@@

Posted by @@USERNAME@@(@@USEREMAIL@@) on @@UPLOADTIME@@.
"""
