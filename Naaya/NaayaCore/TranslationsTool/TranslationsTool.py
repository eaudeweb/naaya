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

"""
This module contains the class that implements a message catalog
for Naaya CMF messages (labels).

This is a core tool of the Naaya CMF.
Every portal B{must} have an object of this type inside.
"""

#Python import
import base64
import re
from urllib import quote
import locale

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Localizer.MessageCatalog import MessageCatalog

#Product imports
from Products.NaayaCore.constants import *

def manage_addTranslationsTool(self, languages=None, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    if languages is None: languages = []
    ob = TranslationsTool(ID_TRANSLATIONSTOOL, TITLE_TRANSLATIONSTOOL)
    self._setObject(ID_TRANSLATIONSTOOL, ob)
    self._getOb(ID_TRANSLATIONSTOOL).loadDefaultData(languages)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class TranslationsTool(MessageCatalog):
    """
    Class that implements the tool.
    """

    meta_type = METATYPE_TRANSLATIONSTOOL
    icon = 'misc_/NaayaCore/TranslationsTool.gif'

    manage_options = (
        MessageCatalog.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        MessageCatalog.__dict__['__init__'](self, id, title, sourcelang='en', languages=['en'])

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, languages):
        """
        Creates default stuff.
        I{(Nothing for the moment.)}
        """
        pass

    def get_msg_translations(self, message='', lang=''):
        """
        Returns the translation of the given message in the given language.
        @param message: the message
        @type message: string
        @param lang: language code
        @type lang: string
        """
        mesg = self._messages.get(message, None)
        if mesg:
            return mesg.get(lang, '')

    def msgEncode(self, message):
        """
        Encodes a message in order to be passed as parameter in
        the query string.
        """
        return quote(self.message_encode(message))

    def tt_get_messages(self, query, skey, rkey):
        """
        Returns a list of messages, filtered and sorted according with
        the given parameters.
        @param query: query against the list of messages
        @type query: string
        @param skey: the sorting key
        @type skey: string
        @param rkey: indicates if the list must be reversed
        @type rkey: string
        """
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
        default_locale = locale.setlocale(locale.LC_ALL)
        try: locale.setlocale(locale.LC_ALL, 'en')
        except: locale.setlocale(locale.LC_ALL, 'en_EN')
        t.sort(lambda x, y: locale.strcoll(x[0], y[0]))
        locale.setlocale(locale.LC_ALL, default_locale)
        if rkey: t.reverse()
        msgs = [val for (key, val) in t]
        return msgs

    def tt_get_languages_mapping(self):
        """
        Returns the languages mapping without the english language.
        Remove the entry for the 'code' = 'en'.
        """
        d = []
        for x in self.get_languages_mapping():
            if x['code'] != 'en':
                d.append(x)
        return d

InitializeClass(TranslationsTool)
