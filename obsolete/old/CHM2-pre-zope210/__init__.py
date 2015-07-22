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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Dragos Chirila

#Python imports
from os.path import join

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *
from Products.NaayaCore.managers.utils import file_utils
from managers.config_parser import config_parser
import CHMSite

def initialize(context):
    """ """

    #register classes
    context.registerClass(
        CHMSite.CHMSite,
        permission = PERMISSION_ADD_CHMSITE,
        constructors = (
                CHMSite.manage_addCHMSite_html,
                CHMSite.manage_addCHMSite,
                ),
        icon = 'www/Site.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
}

#process config.xml file
content_urls = {}
config = config_parser()
config_handler, error = config_parser().parse(file_utils().futRead(join(CHM2_PRODUCT_PATH, 'skel', 'config.xml'), 'r'))
if config_handler is not None:
    if config_handler.root.urls is not None:
        for item in config_handler.root.urls.entries:
            if not content_urls.has_key(item.meta_type):
                content_urls[item.meta_type] = []
            content_urls[item.meta_type].append(item.property)

def get_content_urls(self):
    return content_urls

CHMSite.CHMSite.get_content_urls = get_content_urls

