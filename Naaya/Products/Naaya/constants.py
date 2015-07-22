"""
This module contains global constants.
"""


import Globals


NAAYA_PRODUCT_NAME = 'Naaya'
NAAYA_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADD_SITE = 'Naaya - Add Naaya Site objects'
PERMISSION_ADD_FOLDER = 'Naaya - Add Naaya Folder objects'

METATYPE_NYSITE = 'Naaya Site'
METATYPE_FOLDER = 'Naaya Folder'
METATYPE_MEETING = 'Naaya Meeting'

LABEL_NYFOLDER = 'Folder'

# Default language as described in ISO 639
# ISO 639 is the set of international standards that lists short codes
# of two to four letters for language name; see languages.txt in naaya.i18n
DEFAULT_PORTAL_LANGUAGE_CODE = 'en'
DEFAULT_PORTAL_LANGUAGE_NAME = 'English'
DEFAULT_SORTORDER = 100
DEFAULT_MAILSERVERNAME = 'localhost'
DEFAULT_MAILSERVERPORT = 25

PREFIX_SITE = 'portal'
PREFIX_FOLDER = 'fol'

ID_IMAGESFOLDER = 'images'
WRONG_PASSWORD = 'Current password is not correct. Changes NOT saved.'

MESSAGE_ROLEADDED = 'Role(s) successfully granted to user ${user}'
MESSAGE_ROLEREVOKED = 'Role(s) successfully revoked to selected user(s)'
MESSAGE_USERADDED = 'User successfully added. Now you can assign a role to this account.'
MESSAGE_USERMODIFIED = 'User\'s credentials saved'

NYEXP_SCHEMA_LOCATION = 'http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaDocuments/schemas/naaya/naaya-nyexp-1.0.0.xsd'

JS_MESSAGES = [
# datetime_js
    u'Today',
    u'Yesterday',
    u'Tomorrow',
    u'Calendar',
    u'Cancel',
# calendar_js
    (u'January February March April May June July '
     u'August September October November December'),
     u'S M T W T F S',
# portal_map
    u'Show All',
    u'Hide All',
    u'Type location address',
    u'Type keywords to filter locations',
    u'close',
# folder_listing.zpt error messages
    u'Please select one or more items to copy.',
    u'Please select one or more items to cut.',
    u'Please select one or more items to delete.',
    u'Please select one or more items to rename.',
# Ajax file upload (CHM NyMunicipality)
    u'Replace picture',
# glossary widget, jquery-ui dialog
    u'Close',
]
