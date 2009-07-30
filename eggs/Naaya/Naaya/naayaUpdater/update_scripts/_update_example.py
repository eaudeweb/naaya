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
# Andrei Laza, Eau de Web


#Python imports

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY

class UpdateExample(UpdateScript):
    """ Update example script  """
    id = 'update_example'
    title = 'Example of update script'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Aug 1, 2009')
    authors = ['Jane Doe']
    #priority = PRIORITY['LOW']
    description = 'This is an example, change this description when implementing an update.'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()


