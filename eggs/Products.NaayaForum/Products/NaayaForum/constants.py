"""
This module contains global constants.
"""

#Python imports
import os
#Product imports

NAAYAFORUM_PRODUCT_NAME = 'NaayaForum'
NAAYAFORUM_PRODUCT_PATH = os.path.dirname(os.path.abspath(__file__))

PERMISSION_ADD_FORUM = 'Add Naaya Forum'
PERMISSION_MODIFY_FORUMTOPIC = 'Add/Edit/Delete Naaya Forum Topic'
PERMISSION_ADD_FORUMMESSAGE = 'Add Naaya Forum Message'
PERMISSION_MODIFY_FORUMMESSAGE = 'Edit/Delete Forum Message'

METATYPE_NYFORUM = 'Naaya Forum'
METATYPE_NYFORUMTOPIC = 'Naaya Forum Topic'
METATYPE_NYFORUMMESSAGE = 'Naaya Forum Message'

LABEL_NYFORUM = 'Forum'
LABEL_NYFORUMTOPIC = 'Topic'
LABEL_NYFORUMMESSAGE = 'Message'

PREFIX_NYFORUM = 'frm'
PREFIX_NYFORUMTOPIC = 'tpc'
PREFIX_NYFORUMMESSAGE = 'msg'

DEFAULT_MAX_FILE_SIZE = 1048576 #1 Mega
