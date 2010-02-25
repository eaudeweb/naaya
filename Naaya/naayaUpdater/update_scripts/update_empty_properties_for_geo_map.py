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
# Valentin Dumitru, Eau de Web


#Python imports

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY

class UpdateLandscapeType(UpdateScript):
    """ Update script  """
    id = 'update_empty_properties_for_geo_map'
    title = 'Update landscape_type and administrative_level from "" to "Unspecified"'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Feb 25, 2010')
    authors = ['Valentin Dumitru']
    #priority = PRIORITY['LOW']
    description = 'Update landscape_type and administrative_level from "" to "Unspecified"'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        for ob in portal.getCatalogedObjects():
            if hasattr(ob, 'landscape_type') and ob.landscape_type == '':
                ob.landscape_type ='Unspecified'
            if hasattr(ob, 'administrative_level') and ob.administrative_level == '':
                ob.administrative_level ='Unspecified'
        return True


