
import itertools

from naaya.core.zope2util import ofs_walk
from Products.naayaUpdater.updates import UpdateScript
from naaya.core.utils import force_to_unicode

from naaya.i18n.portal_tool import NaayaI18n, manage_addNaayaI18n
from naaya.i18n.LocalPropertyManager import LocalAttribute


class LocalizerToNaayaI18n(UpdateScript):
    title = 'Complete migration from Products.Localizer to naaya.i18n'
    creation_date = 'Jun 24, 2011'
    authors = ['Mihnea Simian']
    description = ('Moves Localizer data to a new naaya.i18n instance. '
                   'Performs Cleanup')

    def _update(self, portal):
        """
        Summary of update:
         * test for portal_i18n existance, if true, skip portal
         * get languages and default language
         * create portal_i18n, place it in portal
         * copy message translations
         * fix localized properties
         * delete Localizer and portal_translations

        """
        if isinstance(portal.getPortalI18n(), NaayaI18n):
            self.log.debug("Portal already uses naaya.i18n, skipping")
            return True

        self.log.debug("Creating portal_i18n and copying message catalog data")
        localizer = portal._getOb('Localizer', None)
        portal_trans = portal._getOb('portal_translations')
        if localizer is None:
            self.log.error("Localizer not found")
            return False
        if portal_trans is None:
            self.log.error("Portal Translations not found")
            return False

        languages = [ (x, localizer.get_language_name(x)) for
                      x in localizer.get_languages() ]
        def_lang = localizer.get_default_language()
        self.log.debug('Found languages: %r, default: %s', languages, def_lang)

        manage_addNaayaI18n(portal, languages)
        portal.getPortalI18n().manage_changeDefaultLang(def_lang)

        message_cat = portal.getPortalI18n().get_message_catalog()
        (msg_cnt, trans_cnt) = (0, 0)
        for (msgid, trans) in portal_trans._messages.items():
            if isinstance(msgid, str):
                msgid = force_to_unicode(msgid)
            msg_cnt += 1
            for lang in trans:
                if lang != 'note':
                    trans_cnt += 1
                    if isinstance(trans[lang], unicode):
                        translation = trans[lang]
                    elif isinstance(trans[lang], str):
                        translation = force_to_unicode(trans[lang])
                    else:
                        self.log.error(("Unacceptable type '%s' found for "
                                        "translation") % type(trans[lang]))
                        self.log.error("Migration cancelled")
                        return False
                    message_cat.edit_message(msgid, lang, translation)
        self.log.debug('%d msg ids copied, a total of %d translation mappings.'
                       % (msg_cnt, trans_cnt))

        # Fix local properties:
        # * remove translations with None-index (instead of language code)
        # * add existent properties in _local_properties_metadata
        # * remove blank/emptystring translations
        # Clean up any LocalAttribute-s on instances
        localprops_cnt = 0
        all_objects = itertools.chain([portal], ofs_walk(portal))
        for obj in all_objects:
            for (key, value) in obj.__dict__.items():
                if isinstance(value, LocalAttribute):
                    self.log.debug("Found: %r.%s", obj, key)
                    localprops_cnt += 1
                    delattr(object, key)
            _local_properties = getattr(obj, '_local_properties', None)
            if _local_properties is not None:
                for (property, trans) in _local_properties.items():
                    if property not in obj._local_properties_metadata:
                        obj.set_localproperty(property, 'string')
                    for (lang, translation) in trans.items():
                        if lang is None or not translation:
                            del trans[lang]

        self.log.debug("%d LocalAttribute-s deleted from OFS" % localprops_cnt)

        # Clean up and delete localizer
        localizer.manage_beforeDelete(localizer, portal)
        portal._delObject('Localizer')
        portal._delObject('portal_translations')
        self.log.debug('Localizer and Portal translations removed, '
                       'migration is complete!')
        return True
