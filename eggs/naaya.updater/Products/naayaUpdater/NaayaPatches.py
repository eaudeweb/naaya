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
# Alec Ghica, Eau de Web
# Cornel Nitu, Eau de Web

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
