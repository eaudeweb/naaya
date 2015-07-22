# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Author(s):
# Alexandru Ghica, Adriana Baciu - Finsiel Romania


#Python imports
from os.path import join


#product name
DOCMANAGER_PRODUCT_NAME = 'Finshare'
try:
    DOCMANAGER_PRODUCT_PATH = join(SOFTWARE_HOME, 'Products', DOCMANAGER_PRODUCT_NAME)
    DOCMANAGER_PRODUCT_IMAGES_PATH = join(DOCMANAGER_PRODUCT_PATH, 'images')
    f = open(join(DOCMANAGER_PRODUCT_IMAGES_PATH, 'copy.gif'), 'rb')
    f.close()
    del f
except IOError:
    try:
        DOCMANAGER_PRODUCT_PATH = join(INSTANCE_HOME, 'Products', DOCMANAGER_PRODUCT_NAME)
        DOCMANAGER_PRODUCT_IMAGES_PATH = join(DOCMANAGER_PRODUCT_PATH, 'images')
        f = open(join(DOCMANAGER_PRODUCT_IMAGES_PATH, 'copy.gif'), 'rb')
        f.close()
        del f
    except IOError:
        raise 'Cannot initialize product path', 'Constants.py'
DOCMANAGER_VAR_PATH = join(CLIENT_HOME, DOCMANAGER_PRODUCT_NAME)

#mata types
METATYPE_DMMANAGER = 'Finshare'
METATYPE_DMFOLDER = 'DocFolder'
METATYPE_DMARTICLE = 'DocArticle'
METATYPE_DMFILE = 'DocFile'
METATYPE_DMURL = 'DocURL'
METATYPE_DMNOTIFY = 'DocNotify'

METATYPE_OBJECTS = [METATYPE_DMURL, METATYPE_DMFILE, METATYPE_DMARTICLE]
METATYPE_ALL = [METATYPE_DMFOLDER, METATYPE_DMARTICLE]
#METATYPE_ALL = [METATYPE_DMFOLDER, METATYPE_DMURL, METATYPE_DMFILE, METATYPE_DMARTICLE]

#catalog
DOCMANAGER_CATALOG = 'DocManager_catalog'

#template files
DOCMANAGER_TEMPLATE = 'DocManager_template'
DOCMANAGER_CSS = 'DocManager_style'

#define roles names
DOCMANAGER_ROLE_ADMINISTRATOR = 'DocAdministrator'
DOCMANAGER_ROLE_CONTRIBUTOR = 'DocContributor'

#Permission names
PERMISSION_VIEW_DMOBJECTS =     'Finshare - View Objects'
PERMISSION_PUBLISH_DMOBJECTS =  'Finshare - Publish Objects'
PERMISSION_EDIT_DMOBJECTS =     'Finshare - Edit content'
PERMISSION_DELETE_DMOBJECTS =   'Finshare - Delete content'

PERMISSION_ADD_DOC_FOLDER =     'Finshare - Add folders'
PERMISSION_ADD_DOC_URL =        'Finshare - Add URLs'
PERMISSION_ADD_DOC_ARTICLE =    'Finshare - Add articles'
PERMISSION_ADD_DOC_FILE =       'Finshare - Add files'

PERMISSION_EDIT_USERS = 'Finshare - Manage users'
PERMISSION_CHANGE_PROPERTIES = 'Finshare - Change properties'

PERMISSIONS_ADMINISTRATOR = [PERMISSION_VIEW_DMOBJECTS,
                             PERMISSION_PUBLISH_DMOBJECTS,
                             PERMISSION_EDIT_DMOBJECTS,
                             PERMISSION_DELETE_DMOBJECTS,
                             PERMISSION_ADD_DOC_FOLDER,
                             PERMISSION_ADD_DOC_FILE,
                             PERMISSION_ADD_DOC_ARTICLE,
                             PERMISSION_ADD_DOC_URL,
                             PERMISSION_EDIT_USERS,
                             PERMISSION_CHANGE_PROPERTIES]

PERMISSIONS_CONTRIBUTOR = [PERMISSION_VIEW_DMOBJECTS,
                           PERMISSION_EDIT_DMOBJECTS,
                           PERMISSION_ADD_DOC_FOLDER,
                           PERMISSION_ADD_DOC_ARTICLE,
                           PERMISSION_ADD_DOC_FILE,
                           PERMISSION_ADD_DOC_URL]

PERMISSIONS_ZOPE = ['View management screens',
                    'Add Python Scripts',
                    'Add Documents, Images, and Files',
                    'Delete objects']

##define security constants for items
#ITEM_SECURITY_PUBLIC = 'public'
#ITEM_SECURITY_LIMITED = 'limited'
#ITEM_SECURITY_INTERNAL = 'internal'
#ITEM_SECURITY_TOPSECRET = 'top secret'

#anonymous user label
ANONYMOUS_USER_NAME = 'Anonymous'

#history labels
HISTORY_ITEM_ADDED = 'Item added'
HISTORY_ITEM_MODIFIED = 'Item modified'
HISTORY_ITEM_APPROVED = 'Item approved'
HISTORY_COMMENT_ADDED = 'Comment added'
HISTORY_COMMENT_MODIFIED = 'Comment modified'
HISTORY_COMMENT_DELETED = 'Comment(s) deleted'

#manage options labels
ITEM_MANAGE_OPTION_VIEW = 'View'
ITEM_MANAGE_OPTION_PROPERTIES = 'Properties'
ITEM_MANAGE_OPTION_COMMENTS = 'Comments'
ITEM_MANAGE_OPTION_HISTORY = 'History'
ITEM_MANAGE_OPTION_VESIONS = 'Versions'
ITEM_MANAGE_OPTION_CONTENTTYPES = 'File types'
#ITEM_MANAGE_OPTION_LANGUAGES = 'Languages'
ITEM_MANAGE_OPTIONS_THEMATIC_AREA = 'Thematic Area'

# Exceptions
EXCEPTION_NOTIMPLEMENTED = 'NotImplemented'
EXCEPTION_NOTACCESIBLE = 'NotAccesible'
EXCEPTION_NOTAUTHORIZED = 'Unauthorized'
EXCEPTION_NOTAUTHORIZED_MSG = 'You are not authorized to access this resource'
EXCEPTION_WEBDAV = 'File is locked via WebDAV'

#Errors
ERROR100 = """The firstname must be specified"""
ERROR101 = """The lastname must be specified"""
ERROR102 = """An username must be specified"""
ERROR103 = """Password and confirmation must be specified"""
ERROR104 = """Enter an email address. This is necessary in case the password
                is lost. We respect your privacy, and will not give the address
                away to any third parties or expose it anywhere."""
ERROR105 = """The login name you selected is already in use or is not valid. Please choose another."""
ERROR106 = """Password and confirmation do not match"""
#ERROR107 = 'Illegal domain specification'
ERROR108 = """No users specified"""
#ERROR109 = 'The specified user does not exist'
#ERROR110 = 'The location you have specified is not valid'
#ERROR111 = 'No users specified'
#ERROR112 = 'No roles specified'
ERROR113 = """Member with this email address already exists."""
ERROR114 = """Member with this name address already exists."""
ERROR115 = """Enter your current password."""
ERROR116 = """Invalid password. Please insert the corect password."""
ERROR117 = """I'm sorry. We do not have record of your email. 
            Please ensure that you are entering the proper email and try again. 
            If you continue to have problems, contact customer service at:"""

ERROR300 = 'Error parsing xml file: %s'

#Info messages
MESSAGE_SAVEDCHANGES = 'Saved changes. (%s)'

#History
HISTORY_ADD = "Object added"
HISTORY_PASTE = "Object pasted"
HISTORY_EDIT = "Object's property changed"
HISTORY_UPLOAD = "New file uploaded"
HISTORY_NEW_VERSION = "New object's version created"
HISTORY_EDIT_VERSION = "Existing object's version modified"
HISTORY_COMMENT = "Comment added"

#Download comments
DOWNLOAD_POSSIBLE = "Can be downloaded"
DOWNLOAD_IMPOSSIBLE = "No download possible"

#Status values
DOCMANAGER_STATUS = ['Draft', 'Final', 'Released']

#ContentTypes
DOCMANAGER_CONTENTETYPES = (("text/plain", "TXT", "text.gif"), \
                            ("text/html", "HTML", "html.gif"), \
                            ("text/xml", "XML", "xml.gif"), \
                            ("image/gif", "GIF", "image.gif"), \
                            ("image/pjpeg", "JPEG", "image.gif"), \
                            ("image/jpeg", "JPEG", "image.gif"), \
                            ("image/jpg", "JPEG", "image.gif"), \
                            ("image/bmp", "BMP", "image.gif"), \
                            ("image/png", "PNG", "image.gif"), \
                            ("image/x-png", "PNG", "image.gif"), \
                            ("application/octet-stream", "BINARY", "stream.gif"), \
                            ("application/msword", "DOC", "word.gif"), \
                            ("application/msaccess", "MDB", "mdb.gif"), \
                            ("application/pdf", "PDF", "pdf.gif"), \
                            ("application/vnd.ms-powerpoint", "PPT", "ppt.gif"), \
                            ("application/vnd.ms-excel", "XLS", "excel.gif"), \
                            ("undefined", "Unknown", "none.gif"), \
                            ("application/x-zip-compressed", "ZIP", "zip.gif") \
                           )
                           
#Thematic area list
    
THEMATIC_AREA = ['Documenti di Specifica',
                 'Documenti di Progettazione',
                 'Documenti di Realizzazione',
                 'Documenti di Test',
                 'Documenti di Verifica e di Accetazzione',
                 'Comunicazioni Interne',
                 'Comunicazioni Esterne',
                 'Documenti Contrattuali',
                 'Documenti di Formazione',
                 'Documenti di Gestione e Rapporti con i Clienti',
                 'Documenti Metodologici',
                 'Documenti di Coordinamento, Pianificazione e Controllo',
                 'Documenti di Conduzione Sistemi',
                 'Documenti di Conduzione tecnico-sistemistica',
                 'Documenti sulla Sicurezza Informatica',
                 'Altro']                           

#ZIP module messages
ZIP_DOWNLOAD_FILENAME = 'download.zip'
ZIP_VALID_FILE = 'You must specify a valid file!'
ZIP_CREATED = 'The Documents were successfully created!'
ZIP_HIERARCHICAL = 'The zip file you specified is hierarchical. It contains folders.\nPlease upload a non-hierarchical structure of files.'

#Namespaces for RDF
DOCMANAGER_NAMESPACES = [ \
    'xmlns="http://purl.org/rss/1.0/"', \
    'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"', \
    'xmlns:dc="http://purl.org/dc/elements/1.1/"', \
                        ]

#Default languages
#LANGUAGES_LIST = ['Bulgarian', 'Czech', 'Danish', 'Dutch', 'Estonian', 'English', 'Finnish', 'French', 'German', 'Greek', 'Hungarian', 'Icelandic', 'Italian', 'Latvian', 'Lithuanian', 'Norwegian', 'Polish', 'Portuguese', 'Romanian', 'Slovak', 'Slovenian', 'Spanish', 'Swedish', 'Turkish']

#Preselected language
PRESELECTED_LANGUAGE = 'English'