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

from AccessControl import ClassSecurityInfo
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateImageContainer(UpdateScript):
    """ Update add forum script  """
    title = 'Update imagecontainer portal property'
    creation_date = 'Jul 23, 2010'
    authors = ['Cornel Nitu']
    description = 'Updates the imageContainer propery on portal'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.log.debug('Updating imageContainer to %s' % portal.title_or_id())
        setattr(portal, 'imageContainer', NyImageContainer(portal.getImagesFolder(), False))
#        for doc in portal.getCatalogedObjects('Naaya Document'):
#            setattr(doc, 'imageContainer', NyImageContainer(doc, True))
        return True
