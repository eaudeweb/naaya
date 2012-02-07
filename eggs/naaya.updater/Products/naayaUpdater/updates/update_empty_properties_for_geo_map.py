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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateLandscapeType(UpdateScript):
    """ Update script  """
    title = 'Update landscape_type and administrative_level from missing or "" to "Unspecified" + other corrections'
    creation_date = 'Feb 7, 2012'
    authors = ['Valentin Dumitru']
    description = 'Update landscape_type and administrative_level from missing or "" to "Unspecified" + other corrections'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        replacements = {
            'Unspecified': ['', 'unspecified', [u'unspecified'], u"[u'unspecified']"],
            'Local': ['local'],
            'Sub-Global': ['Sub-global', 'sub-global'],
            'Regional': ['regional']

        }
        for ob in portal.getCatalogedObjects(meta_type='Naaya Contact'):
            changed = False
            if not hasattr(ob, 'landscape_type') or ob.landscape_type == '':
                ob._setLocalPropValue('landscape_type', 'en', 'Unspecified')
                self.log.debug('Landscape type set to "Unspecified" for %s' %
                    ob.absolute_url())
                changed = True

            if not hasattr(ob, 'administrative_level'):
                self.log.debug('Landscape type set to "Unspecified" for %s' %
                    ob.absolute_url())
                ob._setLocalPropValue('administrative_level', 'en', 'Unspecified')
                changed = True

            else:
                for key, values in replacements.items():
                    if ob.administrative_level in values:
                        self.log.debug('Administrative level: replaced "%s" by "%s" for %s' % (
                            ob.administrative_level, key, ob.absolute_url()))
                        ob._setLocalPropValue('administrative_level', 'en', key)
                        changed = True

                if ob.administrative_level != ob.administrative_level.strip():
                    self.log.debug('Administrative level: replaced "%s" by "%s" for %s' % (
                        ob.administrative_level, ob.administrative_level.strip(),
                        ob.absolute_url()))
                    ob._setLocalPropValue('administrative_level', 'en', ob.administrative_level.strip())
                    changed = True
            if changed:
                portal.recatalogNyObject(ob)
        return True
