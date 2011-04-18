from time import time
import sys
import os, popen2
from StringIO import StringIO

from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG, WARNING

try:
    from Products.PageTemplates.GlobalTranslationService import \
                                                    setGlobalTranslationService
    patch_trans_service = True
except ImportError:
    patch_trans_service = False

from Products.NaayaCore.TranslationsTool.TranslationsTool import TranslationsTool
from Products.Localizer.LocalPropertyManager import LocalPropertyManager

from Products.Localizer.MessageCatalog import MessageCatalog
from itools.gettext import POFile
from Globals import PersistentMapping

# Localizer patch crash pagetamplates. Restore pagetemplate.StringIO
from zope.pagetemplate import pagetemplate
pagetemplate.StringIO = StringIO

#patch for MessageCatalog
def po_import(self, lang, data):
    """ """
    messages = self._messages

    # Load the data
    po = POFile(string=data)
    for msgid in po.get_msgids():
        if isinstance(msgid, unicode):  msgid = msgid.encode('utf-8')
        if msgid:
            msgstr = po.get_msgstr(msgid) or ''
            if not messages.has_key(msgid):
                messages[msgid] = PersistentMapping()
            messages[msgid][lang] = msgstr

        # Set the encoding (the full header should be loaded XXX)
        self.update_po_header(lang, charset=po.get_encoding())

MessageCatalog.po_import = po_import

#patch for Localizer
def _setLocalPropValue(self, id, lang, value):
    # Get previous value
    old_value, timestamp = self.get_localproperty(id, lang)
    # Update value only if it is different
    if value != old_value:
        properties = self._local_properties.copy()
        if not properties.has_key(id):
            properties[id] = {}
        properties[id][lang] = (value, time())
        self._local_properties = properties

LocalPropertyManager._setLocalPropValue = _setLocalPropValue

class GlobalTranslationService:
    def translate(self, domain, msgid, *args, **kw):
        if domain == 'default':
            domain = 'portal_translations'
        context = kw.get('context')
        if context is None: return msgid
        translation_service = getattr(context, domain, None)
        if translation_service is not None:
            if isinstance(translation_service, TranslationsTool):
                return translation_service.translate(domain, msgid, *args, **kw)
        return msgid

def initialize(context):
    """ """
    if patch_trans_service is True:
        setGlobalTranslationService(GlobalTranslationService())

LOG('naayaHotfix', DEBUG, 'Patch for Localizer and other stuff')

#apply patches from the patches folder
from patches import extfile_patch

extfile_patch.patch_fs_paths_and_pack()
extfile_patch.patch_extfile_extension()
