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
        msgs_append = msgs.append
        langs = self.tt_get_languages_mapping()
        if skey == 'msg': skey = 0
        try: regex = re.compile(query.strip().lower())
        except: regex = re.compile('')
        for m, t in self._messages.items():
            if regex.search(m.lower()):
                e = [self.utToUtf8(m)]
                i = 1
                for lang in langs:
                    if skey == lang['code']: skey = i
                    e.append(len(t.get(lang['code'], '').strip())>0)
                    i = i + 1
                msgs_append(tuple(e))
        #sort messages
        t = [(x[skey], x) for x in msgs]
        if skey == 0:
            #sort by message
            default_locale = locale.setlocale(locale.LC_ALL)
            try: locale.setlocale(locale.LC_ALL, 'en')
            except: locale.setlocale(locale.LC_ALL, 'en_US')
            t.sort(lambda x, y: locale.strcoll(x[0], y[0]))
            locale.setlocale(locale.LC_ALL, default_locale)
        else:
            #sort by translation status
            t.sort()
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

    security.declareProtected('Manage messages', 'xliff_export')
    def xliff_export(self, x, export_all=1, REQUEST=None, RESPONSE=None):
        """ Exports the content of the message catalog to an XLIFF file
        """
        orglang = self._default_language
        from DateTime import DateTime
        from Products.Localizer.MessageCatalog import md5text
        from cgi import escape
        r = []
        # alias for append function. For optimization purposes
        r_append = r.append
        # Generate the XLIFF file header
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s_%s_%s.xlf"' % (self.id,
                                                                    orglang,
                                                                    x))

        r_append('<?xml version="1.0" encoding="UTF-8"?>')
        # Version 1.1 of the DTD is not yet available - use version 1.0
        r_append('<!DOCTYPE xliff SYSTEM "http://www.oasis-open.org/committees/xliff/documents/xliff.dtd">')
        # Force a UTF-8 char in the start
        r_append(u'<!-- XLIFF Format Copyright \xa9 OASIS Open 2001-2003 -->')
        r_append('<xliff version="1.0">')
        r_append('<file')
        r_append('original="/%s"' % self.absolute_url(1))
        r_append('product-name="Localizer"')
        r_append('product-version="1.1.x"')
        r_append('datatype="plaintext"')
        r_append('source-language="%s"' % orglang)
        r_append('target-language="%s"' % x)
        r_append('date="%s"' % DateTime().HTML4())
        r_append('>')
        r_append('<header>')
#       r_append('<phase-group>')
#       r_append('<phase ')
#       r_append('phase-name="%s"' % REQUEST.get('phase_name', ''))
#       r_append('process-name="Export"')
#       r_append('tool="Localizer"')
#       r_append('date="%s"' % DateTime().HTML4())
#       r_append('company-name="%s"' % REQUEST.get('company_name', ''))
#       r_append('job-id="%s"' % REQUEST.get('job_id', ''))
#       r_append('contact-name="%s"' % REQUEST.get('contact_name', ''))
#       r_append('contact-email="%s"' % REQUEST.get('contact_email', ''))
#       r_append('/>')
#       r_append('</phase-group>')
        r_append('</header>')
        r_append('<body>')

        # Get the messages, and perhaps its translations.
        d = {}
        for msgkey, transunit in self._messages.items():
            # if export_all=1 export all messages otherwise export
            # only untranslated messages
            try:
                tr_unit = transunit[x]
            except KeyError:
                tr_unit = ''

            if int(export_all) == 1 or (int(export_all) == 0 and tr_unit == ''):
                d[msgkey] = tr_unit
            else:
                d[msgkey] = ""

            if d[msgkey] == "":
                d[msgkey] = msgkey

        # Generate sorted msgids to simplify diffs
        dkeys = d.keys()
        dkeys.sort()
        for msgkey in dkeys:
            transunit = self._messages[msgkey]
            r_append('<trans-unit id="%s">' % md5text(msgkey))
            r_append(' <source>%s</source>' % escape(msgkey))
            r_append(' <target>%s</target>' % escape(d[msgkey]))
            if transunit.has_key('note') and transunit['note']:
                r_append(' <note>%s</note>' % escape(transunit['note']))
            r_append('</trans-unit>')

        r_append('</body>')
        r_append('</file>')
        r_append('</xliff>')

        r2 = []
        for x in r:
            if isinstance(x, unicode):
                r2.append(x.encode('utf-8'))
            else:
                r2.append(x)

        return '\r\n'.join(r2)

InitializeClass(TranslationsTool)
