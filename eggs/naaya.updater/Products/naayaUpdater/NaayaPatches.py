from Globals import PersistentMapping
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

from Products.NaayaCore.TranslationsTool.TranslationsTool import TranslationsTool

security = ClassSecurityInfo()

def patchForBIODIVTranslations(self, REQUEST=None):
    """ """
    langs = self.tt_get_languages_mapping()
    for m, t in self._messages.items():
        if isinstance(m, unicode):
            try:
                self.message_del(m)
            except KeyError, err:
                print err
            m = m.encode('utf-8')
            self._messages[m] = PersistentMapping()
            for lang in langs:
                self._messages[m][lang['code']] = t.get(lang['code'], '')
    self._p_changed = 1
    return 'done'

TranslationsTool.patchForBIODIVTranslations = patchForBIODIVTranslations
security.declareProtected(view_management_screens, 'patchForBIODIVTranslations')
security.apply(TranslationsTool)
