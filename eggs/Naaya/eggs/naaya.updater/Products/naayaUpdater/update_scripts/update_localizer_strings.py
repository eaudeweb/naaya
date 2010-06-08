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
# David Batranu, Eau de Web


#Python imports
import traceback
from BeautifulSoup import BeautifulStoneSoup

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY

class UpdateLocalizerStrings(UpdateScript):
    """ Unescape HTMLEntities in translations """
    id = 'update_localizer_strings'
    title = 'Unescape HTMLEntities in translations'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Jan 25, 2010')
    authors = ['David Batranu']
    #priority = PRIORITY['LOW']
    description = ('Unescape HTMLEntities in translated portal messages.'
                   'This is needed for the new Localizer used by Naaya since Zope 2.10')
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        tt = portal.getPortalTranslations()
        unescaped_messages = {}
        for message, translations in tt._messages.items():
            unescaped_translations = {}
            for lang_code, trans in translations.items():
                try:
                    unescaped_trans = self.unescape(trans)
                    unescaped_translations[lang_code] = unescaped_trans
                    self.log.debug('Unescaped "%s" to "%s"' % (repr(trans), repr(unescaped_trans)))
                except Exception, e:
                    unescaped_translations[lang_code] = trans
                    self.log.debug('Could not unescape "%s" (%s)' % (repr(trans), str(e)))
                    self.log.error(traceback.format_exc())
            unescaped_messages[message] = unescaped_translations
        tt._messages = unescaped_messages
        tt._p_changed = 1
        self.log.debug('Unescaped translations.')
        return True

    def unescape(self, s):
        ENITITES = BeautifulStoneSoup.HTML_ENTITIES
        unescaped = BeautifulStoneSoup(s, convertEntities=ENITITES)
        try:
            unescaped = [unicode(str(x), 'utf-8') for x in unescaped]
            return ''.join(unescaped)
        except:
            return s
