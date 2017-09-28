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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web


#Python imports
import os
from os.path import join
from StringIO import StringIO
from urllib2 import urlopen
from urllib import urlencode

import simplejson as json

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript

from Products.Naaya import NySite as NySite_module
from Products.Naaya.managers.skel_parser import skel_parser
from Products.NaayaCore.managers.utils import html_diff, normalize_template
from Products.naayaUpdater.utils import (convertLinesToList, convertToList,
    get_template_content, readFile)
from utils import physical_path, list_folders_with_custom_index

default_service_url = 'http://speaker.edw.ro/css_diff?format=json'
service_url = os.environ.get('NY_UPDATER_CSS_URL', default_service_url)

class UpdateCSS(UpdateScript):
    """ List custom objects """
    title = 'List custom objects'
    authors = ['Alex Morega']
    description = "Shows objects that have been customized (at the moment, just folders with custom indexes)"
    creation_date = 'Nov 26, 2009'

    def _update(self, portal):
        self.log.debug(physical_path(portal))

        t = 'folder index: <a href="%(url)s/manage_main">%(text)s</a>'
        for folder in list_folders_with_custom_index(portal):
            self.log.info(t % {'url': folder.absolute_url(),
                               'text': physical_path(folder)})

        return True
