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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python import
import base64
import re
from urllib import quote

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Localizer.MessageCatalog import MessageCatalog

#Product imports
from Products.NaayaCore.constants import *

def manage_addTranslationsTool(self, languages=None, REQUEST=None):
    """ """
    if languages is None: languages = []
    ob = TranslationsTool(ID_TRANSLATIONSTOOL, TITLE_TRANSLATIONSTOOL)
    self._setObject(ID_TRANSLATIONSTOOL, ob)
    self._getOb(ID_TRANSLATIONSTOOL).loadDefaultData(languages)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class TranslationsTool(MessageCatalog):
    """ """

    meta_type = METATYPE_TRANSLATIONSTOOL
    icon = 'misc_/NaayaCore/TranslationsTool.gif'

    manage_options = (
        MessageCatalog.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        MessageCatalog.__dict__['__init__'](self, id, title, sourcelang='en', languages=['en'])

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, languages):
        #creates default stuff
        pass

    def get_msg_translations(self, message='', lang=''):
        mesg = self._messages.get(message, None)
        if mesg:
            return mesg.get(lang, '')

    def msgEncode(self, message):
        return quote(self.message_encode(message))

    def get_all_messages(self, message, lang, regex, batch_start):
        """ return all messages"""
        res = []
        messages = self.filter(message, lang, 1, regex, batch_start)
        for i in messages['messages']:
            res.append(i['message'])
        return res

    #new stuff
    def tt_get_messages(self, query, skey, rkey):
        #returns all messages
        msgs = []
        langs = self.tt_get_languages_mapping()
        if skey == 'msg': skey = 0
        try: regex = re.compile(query.strip().lower())
        except: regex = re.compile('')
        msgs_append = msgs.append
        for m, t in self._messages.items():
            if regex.search(m.lower()):
                e = [m]
                i = 1
                for lang in langs:
                    if skey == lang['code']: skey = i
                    e.append(len(t.get(lang['code'], '').strip())>0)
                    i = i + 1
                msgs_append(tuple(e))
        t = [(x[skey], x) for x in msgs]
        t.sort()
        if rkey: t.reverse()
        msgs = [val for (key, val) in t]
        return msgs

    def tt_get_languages_mapping(self):
        #returns the languages mapping without the english language
        #remove the entry for the 'code' = 'en'
        d = []
        for x in self.get_languages_mapping():
            if x['code'] != 'en':
                d.append(x)
        return d

InitializeClass(TranslationsTool)
