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
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty

from Products.Localizer.MessageCatalog import MessageCatalog
from itools.gettext import POFile
from Globals import PersistentMapping
import App

# Localizer patch crash pagetamplates. Restore pagetemplate.StringIO
from zope.pagetemplate import pagetemplate
if pagetemplate.StringIO != StringIO:
    LOG('naayaHotfix', INFO, "Undoing damage done by Localizer patching")
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

if App.version_txt.getZopeVersion() < (2, 12):
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
else:
    def initialize(context):
        pass

#apply patches from the patches folder
from patches import extfile_patch

extfile_patch.patch_fs_paths_and_pack()
extfile_patch.patch_extfile_extension()
