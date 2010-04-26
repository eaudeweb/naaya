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
# David Batranu, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.Localizer.LocalPropertyManager    import LocalProperty

class CustomContentUpdater(NaayaContentUpdater):
    """ Add new properties to Naaya content types to allow geocoding """

    _properties = NaayaContentUpdater._properties + (
        {'id':'update_meta_type', 'type': 'lines','mode':'w',
         'label': 'Content types to fix'},
        {'id':'update_prop', 'type': 'string','mode':'w',
         'label': 'Property to fix'},

    )
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Fix Content type local property'
        self.description = 'Check if given property is LocalProperty instance for given content-types, and delete it if not.'
        self.update_meta_type = ['Naaya Semide Event',]
        self.update_prop = 'address'

    def _verify_doc(self, doc):
        prop = doc.__dict__.get(self.update_prop, None)
        if prop is None:
            return None
        if isinstance(prop, LocalProperty):
            return None
        return doc

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('Update content %s, property: %s', update.absolute_url(), self.update_prop)
            try:
                delattr(update, self.update_prop)
            except Exception, err:
                logger.debug('[FAILED: %s', err)
            else:
                logger.debug('[DONE]')

def register(uid):
    return CustomContentUpdater(uid)
