#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Persistence.mapping import PersistentMapping

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript
from naaya.core.utils import force_to_unicode

class UpdateLocalizer(UpdateScript):
    """ Update Localizer data structures  """
    title = 'Update Localizer data structures'
    creation_date = 'Jun 3, 2010'
    authors = ['Alex Morega']
    description = ("Update internal data structures of Localizer's "
                   "message catalogue")

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.log.info('updating %r', portal)

        portal_translations = portal.portal_translations
        messages = portal_translations._messages

        for key in messages.keys():
            value = messages[key]

            #if type(key) is str:
            #    old_key = key
            #    key = force_to_unicode(key)
            #    del messages[old_key]
            #    messages[key] = value
            #    self.log.debug('convert key %r to %r', old_key, key)

            if type(value) is dict:
                value = PersistentMapping(value)
                messages[key] = value
                self.log.debug('use PersistentMapping value for key %r', key)

        if type(messages) is dict:
            portal_translations._messages = PersistentMapping(messages)
            self.log.debug('_messages converted to PersistentMapping')

        return True
