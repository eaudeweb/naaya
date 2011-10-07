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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

import ConfigParser
from os.path import join

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Globals import InitializeClass
from OFS.Folder import Folder
from EmailTemplate import addEmailTemplate
import constants

def manage_addTemplatesManager(self, REQUEST=None):
    """ """
    ob = TemplatesManager('email_templates', 'Email templates')
    self._setObject('email_templates', ob)
    zobj = self._getOb('email_templates')
    zobj._loadTemplates()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class TemplatesManager(Folder):
    """ Email templates manager """

    meta_type = 'TemplatesManager'
    icon = 'misc_/CHMRegistrationDec2009/EmailTemplates.gif'

    security = ClassSecurityInfo()

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Reload', 'action': 'reloadTemplates'},
        )
        +
        Folder.manage_options[2:]
    )

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    security.declareProtected(view_management_screens, 'reloadTemplates')
    def reloadTemplates(self, REQUEST=None):
        """ reload email templates """
        self._deleteTemplates()
        self._loadTemplates()
        if REQUEST:
            return self.manage_main(self, REQUEST, update_menu=1)

    security.declarePrivate('_deleteTemplates')
    def _deleteTemplates(self):
        self.manage_delObjects(self.objectIds('Folder'))

    security.declarePrivate('_loadTemplates')
    def _loadTemplates(self):
        """ load default email templates """
        config = ConfigParser.ConfigParser()
        email_templates_dir = join(constants.PRODUCT_PATH, 'zpt', 'email_templates')
        config.read(join(email_templates_dir, 'email_templates.ini'))
        for section in config.sections():
            text = file(join(email_templates_dir, config.get(section, 'source'))).read()
            #create a directory for each language
            lang_dir = config.get(section, 'lang')
            if self._getOb(lang_dir, None) is None:
                self.manage_addFolder(id=lang_dir, title='')
            lang_dir_ob = self._getOb(lang_dir)
            addEmailTemplate(lang_dir_ob,
                            id=config.get(section, 'id'),
                            title=config.get(section, 'title'), 
                            text=text)

InitializeClass(TemplatesManager)