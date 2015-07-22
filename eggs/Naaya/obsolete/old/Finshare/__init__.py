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
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
# Alexandru Ghica, Adriana Baciu - Finsiel Romania


__doc__=""" DocManager """
__version__='$Revision: 1.2 $'[11:-2]

#Python imports

#Zope imports
from ImageFile import ImageFile

#Product imports
from Products.Finshare.DocManager import DocManager, manage_addDocManager, manage_addDocManagerForm


def initialize(context):
    """ initialize the DocManager component """

    #register classes
    context.registerClass(
        DocManager,
#        permission = 'Add DocManager object',
        constructors = (manage_addDocManagerForm, manage_addDocManager),
        icon = 'images/DocManager.gif'
        )

    context.registerHelp()
    context.registerHelpTitle('Finshare')

misc_ = {
    #object icons
    'folder':ImageFile('images/Folder.gif', globals()),
    'folder_marked':ImageFile('images/Folder_marked.gif', globals()),
    'article':ImageFile('images/Article.gif', globals()),
    'article_marked':ImageFile('images/Article_marked.gif', globals()),
    'file':ImageFile('images/File.gif', globals()),
    'file_marked':ImageFile('images/File_marked.gif', globals()),
    'url':ImageFile('images/URL.gif', globals()),
    'url_marked':ImageFile('images/URL_marked.gif', globals()),
    'acl_users.gif':ImageFile('images/acl_users.gif', globals()),

    #layout icons
    'spacer.gif':ImageFile('images/spacer.gif', globals()),
    'plus.gif':ImageFile('images/plus.gif', globals()),
    'minus.gif':ImageFile('images/minus.gif', globals()),
    'square.gif':ImageFile('images/square.gif', globals()),

    'basket':ImageFile('images/Basket.gif', globals()),
    'edit':ImageFile('images/Edit.gif', globals()),

    'xml.png':ImageFile('images/xml.png', globals()),

    'select_all.gif':ImageFile('images/select_all.gif', globals()),
    'copy.gif':ImageFile('images/copy.gif', globals()),
    'cut.gif':ImageFile('images/cut.gif', globals()),
    'paste.gif':ImageFile('images/paste.gif', globals()),
    'delete.gif':ImageFile('images/delete.gif', globals()),
    'download.gif':ImageFile('images/download.gif', globals()),
    'upload.gif':ImageFile('images/upload.gif', globals()),

    'menu-bg.gif':ImageFile('images/menu-bg.gif', globals()),
    'menu-left.gif':ImageFile('images/menu-left.gif', globals()),
    'menu-right.gif':ImageFile('images/menu-right.gif', globals()),
    'menu-left-on.gif':ImageFile('images/menu-left-on.gif', globals()),
    'menu-right-on.gif':ImageFile('images/menu-right-on.gif', globals()),

    'menu-expand.gif':ImageFile('images/menu-expand.gif', globals()),
    'help.gif':ImageFile('images/help.gif', globals()),


    'arrowli.gif':ImageFile('images/arrowli.gif', globals()),
    'arrowlileft.gif':ImageFile('images/arrowlileft.gif', globals()),
    'arrowpath.gif':ImageFile('images/arrowpath.gif', globals()),
    'borderfooter.gif':ImageFile('images/borderfooter.gif', globals()),
    'corner.gif':ImageFile('images/corner.gif', globals()),
    'lefttopline.gif':ImageFile('images/lefttopline.gif', globals()),
    'logo.gif':ImageFile('images/logo.gif', globals()),
    'rightcorner.gif':ImageFile('images/rightcorner.gif', globals()),
    'rightcorner2.gif':ImageFile('images/rightcorner2.gif', globals()),
    'rightcorner3.gif':ImageFile('images/rightcorner3.gif', globals()),
    'topbanner.jpg':ImageFile('images/topbanner.jpg', globals()),
    'topbck.jpg':ImageFile('images/topbck.jpg', globals()),
    'toplines.gif':ImageFile('images/toplines.gif', globals()),
    'topmenuseparator.gif':ImageFile('images/topmenuseparator.gif', globals()),
    'toptab.jpg':ImageFile('images/toptab.jpg', globals())
    }