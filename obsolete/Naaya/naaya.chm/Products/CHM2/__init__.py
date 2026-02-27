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

import os
import Globals
from App.ImageFile import ImageFile

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

    from Products.NaayaCore.LayoutTool.DiskFile import allow_path
    allow_path('Products.CHM2:skel/layout/')
    allow_path('Products.CHM2:skel-chm3/layout/')

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'jquery.ajaxupload.min.js':ImageFile('www/jquery.ajaxupload.min.js', globals()),
    'jquery.Jcrop.min.js':ImageFile('www/jquery.Jcrop.min.js', globals()),
    'tagcloud.css': ImageFile('www/tagcloud.css', globals()),
}

#process config.xml file
content_urls = {}
config = config_parser()
config_handler, error = config_parser().parse(file_utils().futRead(
    os.path.join(CHM2_PRODUCT_PATH, 'skel', 'config.xml'), 'r'))
if config_handler is not None:
    if config_handler.root.urls is not None:
        for item in config_handler.root.urls.entries:
            if not content_urls.has_key(item.meta_type):
                content_urls[item.meta_type] = []
            content_urls[item.meta_type].append(item.property)

def get_content_urls(self):
    return content_urls

CHMSite.CHMSite.get_content_urls = get_content_urls

def chm_bundle_registration():
    """ Register things from skel into the CHM bundle """
    from Products.NaayaCore.FormsTool.bundlesupport import \
        register_templates_in_directory

    def forms_path(skel_name):
        return os.path.join(os.path.dirname(__file__), skel_name, 'forms')

    register_templates_in_directory(forms_path('skel'), 'CHM')
    register_templates_in_directory(forms_path('skel-chm3'), 'CHM3')
