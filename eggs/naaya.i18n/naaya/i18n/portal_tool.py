"""
Here we implement the class of portal_i18n portal tool - NaayaI18n.
A facade of various interconected tools of negotiation, language management,
translation available in naaya.i18n.

"""
import re
from urllib import quote
import logging

from zope.i18n import interpolate
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
try:
    # Zope 2.12
    from App.special_dtml import DTMLFile
    from App.class_init import InitializeClass
except ImportError:
    # Zope <= 2.11
    from Globals import DTMLFile
    from Globals import InitializeClass
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaBase.constants import (MESSAGE_SAVEDCHANGES,
                                          PERMISSION_PUBLISH_OBJECTS)

from constants import (ID_NAAYAI18N, TITLE_NAAYAI18N, METATYPE_NAAYAI18N,
                       PERMISSION_TRANSLATE_PAGES)
from LanguageManagers import NyPortalLanguageManager
from LanguageManagers import normalize_code, get_iso639_name
from NyMessageCatalog import NyMessageCatalog
from NyNegotiator import NyNegotiator
from ImportExport import TranslationsImportExport
from patches import populate_threading_local
from admin_i18n import AdminI18n, message_encode, message_decode
from ExternalService import external_translate
from naaya.core.zope2util import physical_path


log = logging.getLogger('naaya.i18n')


def get_url(url, batch_start, batch_size, regex, lang, empty, **kw):
    params = []
    for key, value in kw.items():
        if value is not None:
            params.append('%s=%s' % (key, quote(value)))

    params.extend(['batch_start:int=%d' % batch_start,
                   'batch_size:int=%d' % batch_size,
                   'regex=%s' % quote(regex),
                   'empty=%s' % (empty and 'on' or '')])

    if lang:
        params.append('lang=%s' % lang)

    return url + '?' + '&amp;'.join(params)


def manage_addNaayaI18n(self, languages=[('en', 'English')],
                        REQUEST=None, RESPONSE=None):
    """
    Add a new NaayaI18n instance (portal_i18n)
    """
    self._setObject(ID_NAAYAI18N,
                    NaayaI18n(ID_NAAYAI18N, TITLE_NAAYAI18N, languages))
    req = REQUEST or self.REQUEST
    if req is not None:
        populate_threading_local(self, req)

    if REQUEST is not None:
        RESPONSE.redirect('manage_main')


class NaayaI18n(SimpleItem):
    """
    Naaya instantiates a **NaayaI18n** object insides its root. This object
    holds the whole internationalization data and operations:
    - management of languages
    - negotiation
    - translating and translation data
    - management of object property localization

    """

    meta_type = METATYPE_NAAYAI18N
    icon = 'misc_/portal_i18n/icon.gif'

    security = ClassSecurityInfo()

    message_debug_list = ()
    message_debug_exception = False

    def __init__(self, id, title, languages=[('en', 'English')]):
        self.id = id
        self.title = title
        n_languages = []
        for (code, name) in languages:
            n_languages.append((normalize_code(code), name))
        self._portal_langs = NyPortalLanguageManager(n_languages)
        lang_codes = tuple([x[0] for x in n_languages])
        catalog = NyMessageCatalog('translation_catalog', 'Translation Catalog',
                                    lang_codes)
        self._catalog = catalog

    ### Getters ###

    security.declarePrivate('get_negotiator')
    def get_negotiator(self):
        """ Return NyNegotiator instance, based on current request """
        return NyNegotiator()

    security.declarePrivate('get_message_catalog')
    def get_message_catalog(self):
        """
        Returns Message Catalog (NyMessageCatalog instance).
        The Message Catalog stores translations for all messages.

        """
        return self._catalog

    security.declarePrivate('get_lang_manager')
    def get_lang_manager(self):
        """
        Returns NyPortalLanguageManager instance in portal, capable
        of managing available languages

        """
        return self._portal_langs

    security.declarePrivate('get_importexport_tool')
    def get_importexport_tool(self):
        """ Returns the import-export wrapper for Message Catalog """
        return TranslationsImportExport(self.get_message_catalog())

    ### More specific language methods ###

    security.declarePublic('get_language_name')
    def get_language_name(self, code):
        """
        Get the language name for 'code'. First it looks up
        languages manually added in portal, then inquiries languages
        in naaya.i18n/languages.txt which finally falls back
        to '???' string

        """
        lang_manager = self.get_lang_manager()
        if code in lang_manager.getAvailableLanguages():
            # try to get name from added langs to site
            return lang_manager.get_language_name(code)
        else:
            # not there, default to languages.txt
            return get_iso639_name(code)

    security.declarePublic('get_languages_mapping')
    def get_languages_mapping(self):
        """
        Returns a list of mappings
        [ {'code': 'lang-code', 'name': 'Language name'}, .. ]
        containing languages currently available in portal.

        """
        langs = list(self._portal_langs.getAvailableLanguages())
        result = []
        default = self._portal_langs.get_default_language()
        for l in langs:
            result.append({'code': l,
                           'name': self.get_language_name(l),
                           'default': l == default})
        return result

    security.declarePrivate('add_language')
    def add_language(self, lang_code, lang_name=None):
        """
        Adds a new supported language in portal_i18n.
        Language code, language name can be any combination.
        If language name is not provided,
        a lookup is being performed in naaya.i18n/languages.txt

        """
        if not lang_code:
            raise ValueError('No language code provided')
        lang_code = normalize_code(lang_code)
        if lang_name is None:
            # search for name directly in languages.txt, obviously not in site
            lang_name = get_iso639_name(lang_code)
        # add language to portal:
        self._portal_langs.addAvailableLanguage(lang_code, lang_name)
        # and to catalog:
        self._catalog.add_language(lang_code)

    security.declarePrivate('del_language')
    def del_language(self, lang):
        """
        Deletes a language from portal_i18n:
         * removes it from available languages
         * removes it from supported languages in message catalog

        """
        self._portal_langs.delAvailableLanguage(lang)
        self._catalog.del_language(lang)

    security.declarePublic('get_selected_language')
    def get_selected_language(self, context=None):
        """
        Performs negotiation and returns selected language based on context
        or grabs context (request) by acquisition.

        """
        if context is None:
            context = self.getSite().REQUEST
        available_languages = self.get_lang_manager().getAvailableLanguages()
        return self.get_negotiator().getLanguage(available_languages, context)

    security.declarePublic('get_default_language')
    def get_default_language(self):
        """ Returns default language in portal """
        return self.get_lang_manager().get_default_language()

    security.declarePublic('change_selected_language')
    def change_selected_language(self, lang, goto=None):
        """ Sets a cookie with a new preferred selected language """
        request = self.REQUEST
        response = request.RESPONSE
        negotiator = self.get_negotiator()

        negotiator.change_language(lang, self, request)

        # Comes back
        if goto is None:
            goto = request['HTTP_REFERER']

        response.redirect(goto)

    ### Translation API ###

    security.declarePublic('get_translation')
    def get_translation(self, msg, _default=None, **kwargs):
        """
        Translate message in selected language using Message Catalog
        and substitute named identifiers with values supplied by kwargs mapping

        Most commonly used - a straight forward complete translation
        in selected language.

        """
        lang = kwargs.get('lang') or self.get_selected_language()
        msg = self.get_message_catalog().gettext(msg, lang, default=_default)
        return interpolate(msg, kwargs)

    ### Private methods for private views

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'external_translate')
    def external_translate(self, message, target_lang):
        """
        Private method that returns a translation based on an external
        service, e.g. Google Translate. Not public because the number of
        requests must not be abusive

        """
        return external_translate(message, target_lang)

    #######################################################################
    # Management screens
    #######################################################################
    def manage_options(self):
        """ """
        options = (
            {'label': u'Messages', 'action': 'manage_messages'},
            {'label': u'Languages', 'action': 'manage_languages'},
            {'label': u'Import', 'action': 'manage_import'},
            {'label': u'Export', 'action': 'manage_export'},
            {'label': u'Debug', 'action': 'manage_debug'},
            ) + SimpleItem.manage_options
        r = []
        for option in options:
            option = option.copy()
            r.append(option)
        return r

    #### Messages Tab ####

    security.declarePublic('get_namespace')
    def get_namespace(self, REQUEST):
        """For the management interface, allows to filter the messages to
        show.
        """
        # Check whether there are languages or not
        languages = self.get_languages_mapping()
        if not languages:
            return {}

        # Input
        batch_start = REQUEST.get('batch_start', 0)
        batch_size = REQUEST.get('batch_size', 15)
        empty = REQUEST.get('empty', 0)
        regex = REQUEST.get('regex', '')
        message = REQUEST.get('msg', None)

        # Build the namespace
        namespace = {}
        namespace['batch_size'] = batch_size
        namespace['empty'] = empty
        namespace['regex'] = regex

        # The language
        lang = REQUEST.get('lang', None) or languages[0]['code']
        namespace['language'] = lang

        # Filter the messages
        query = regex.strip()
        try:
            query = re.compile(query)
        except:
            query = re.compile('')

        messages = []
        for m, t in self.get_message_catalog().messages():
            if query.search(m) and (not empty or not t.get(lang, '').strip()):
                messages.append(m)
        messages.sort()
        # How many messages
        n = len(messages)
        namespace['n_messages'] = n

        # Calculate the start
        while batch_start >= n:
            batch_start = batch_start - batch_size
        if batch_start < 0:
            batch_start = 0
        namespace['batch_start'] = batch_start
        # Select the batch to show
        batch_end = batch_start + batch_size
        messages = messages[batch_start:batch_end]
        # Batch links
        namespace['previous'] = get_url(REQUEST.URL, batch_start - batch_size,
            batch_size, regex, lang, empty)
        namespace['next'] = get_url(REQUEST.URL, batch_start + batch_size,
            batch_size, regex, lang, empty)

        # Get the message
        message_encoded = None
        #translations = {}
        translation = None
        if message is None:
            if messages:
                message = messages[0]
                translation = self.get_message_catalog()\
                                  .gettext(message, lang, '')
                message_encoded = message_encode(message)
        else:
            message_encoded = message
            message = message_decode(message_encoded)
            #translations = self.get_translations(message)
            translation = self.get_message_catalog().gettext(message, lang, '')
        namespace['message'] = message
        namespace['message_encoded'] = message_encoded
        #namespace['translations'] = translations
        namespace['translation'] = translation

        # Calculate the current message
        namespace['messages'] = []
        for x in messages:
            x_encoded = message_encode(x)
            url = get_url(
                REQUEST.URL, batch_start, batch_size, regex, lang, empty,
                msg=x_encoded)
            namespace['messages'].append({
                'message': x,
                'message_encoded': x_encoded,
                'current': x == message,
                'url': url})

        # The languages
        for language in languages:
            code = language['code']
            language['name'] = self.get_translation(unicode(language['name']))
            language['url'] = get_url(REQUEST.URL, batch_start, batch_size,
                regex, code, empty, msg=message_encoded)
        namespace['languages'] = languages

        return namespace

    security.declareProtected('Manage messages', 'manage_messages')
    manage_messages = DTMLFile('zpt/messages', globals())

    security.declareProtected('Manage messages', 'manage_editMessage')
    def manage_editMessage(self, message, language, translation,
                           REQUEST, RESPONSE):
        """Modifies a message.
        """
        message_encoded = message
        message_key = message_decode(message_encoded)
        self.get_message_catalog()\
            .edit_message(message_key, language, translation)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      msg=message_encoded,
                      manage_tabs_message=self.get_translation(u'Saved changes.'))
        RESPONSE.redirect(url)

    security.declareProtected('Manage messages', 'manage_delMessage')
    def manage_delMessage(self, message, REQUEST, RESPONSE):
        """Deletes a message in catalog"""
        message_key = message_decode(message)
        self.get_message_catalog().del_message(message_key)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      manage_tabs_message=self.get_translation(u'Saved changes.'))
        RESPONSE.redirect(url)

    #### Languages Tab ####

    security.declareProtected(view_management_screens, 'manage_languages')
    manage_languages = PageTemplateFile('zpt/languages', globals())

    security.declareProtected(view_management_screens, 'manage_addLanguage')
    def manage_addLanguage(self, language_code, language_name, REQUEST=None):
        """
        Add a new language for this portal.
        """
        self.getSite().gl_add_site_language(language_code, language_name)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    security.declareProtected(view_management_screens, 'manage_delLanguages')
    def manage_delLanguages(self, languages=[], display_order='', REQUEST=None):
        """
        Delete one or more languages. Also handles move up/down language
        in display order.

        """
        if languages:
            self.getSite().gl_del_site_languages(languages)
        if display_order:
            lang_manager = self.get_lang_manager()
            lang_manager.set_display_order(display_order)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    security.declareProtected(view_management_screens,
                              'manage_changeDefaultLang')
    def manage_changeDefaultLang(self, language, REQUEST=None):
        """
        Change the default portal language.
        """
        self.getSite().gl_change_site_defaultlang(language)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    #### Export Tab ####

    security.declareProtected(view_management_screens, 'manage_export')
    manage_export = PageTemplateFile('zpt/export_form', globals())

    security.declareProtected(view_management_screens, 'manage_export_po')
    def manage_export_po(self, language, REQUEST, RESPONSE):
        """ Provides pot/po export file for download """
        export_tool = self.get_importexport_tool()
        if language == 'locale.pot':
            filename = language
        else:
            filename = '%s.po' % language
        RESPONSE.setHeader('Content-type','application/data')
        RESPONSE.setHeader('Content-Disposition',
                           'inline;filename=%s' % filename)
        return export_tool.export_po(language)

    security.declareProtected(view_management_screens, 'manage_export_xliff')
    def manage_export_xliff(self, export_all, language, REQUEST, RESPONSE):
        """ Provides xliff file for download """
        fname = ('%s_%s.xlf'
                 % (self.get_message_catalog()._default_language, language))
        # Generate the XLIFF file header
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s"' % fname)
        export_tool = self.get_importexport_tool()
        return export_tool.export_xliff(language,
                                        export_all=bool(int(export_all)))

    security.declareProtected(view_management_screens, 'manage_export_tmx')
    def manage_export_tmx(self, REQUEST, RESPONSE):
        """ Provides tmx file for download """
        cat = self.get_message_catalog()
        fname = '%s.tmx' % cat.title
        export_tool = self.get_importexport_tool()
        header = export_tool.get_po_header(cat._default_language)
        charset = header['charset']
        # Generate the XLIFF file header
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=%s' % charset)
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s"' % fname)
        return export_tool.export_tmx()

    #### Import Tab ####

    security.declareProtected(view_management_screens, 'manage_import')
    manage_import = PageTemplateFile('zpt/import_form', globals())

    security.declareProtected(view_management_screens, 'manage_import_po')
    def manage_import_po(self, file, language, REQUEST, RESPONSE):
        """ Import PO file into catalog, for an existing language """
        if language not in self.get_lang_manager().getAvailableLanguages():
            raise ValueError('%s language is not available in portal' % language)
        else:
            import_tool = self.get_importexport_tool()
            import_tool.import_po(language, file)
        RESPONSE.redirect('manage_import?save=ok')

    security.declareProtected(view_management_screens, 'manage_import_tmx')
    def manage_import_tmx(self, file, language, REQUEST, RESPONSE):
        raise NotImplementedError("Tmx import is not yet implemented")

    security.declareProtected(view_management_screens, 'manage_import_xliff')
    def manage_import_xliff(self, file, language, REQUEST, RESPONSE):
        raise NotImplementedError("Xliff import is not yet implemented")

    _manage_debug = PageTemplateFile('zpt/debug', globals())
    security.declareProtected(view_management_screens, 'manage_debug')
    def manage_debug(self, REQUEST):
        """ Watch for problematic translation strings """

        if REQUEST.REQUEST_METHOD == 'POST':
            form = REQUEST.form
            self.message_debug_list = form['debug_strings'].splitlines()
            log.info('%s message_debug_list = %r',
                     physical_path(self), self.message_debug_list)
            self.message_debug_exception = bool(form.get('debug_exception', False))

            location = self.absolute_url() + '/manage_debug'
            return REQUEST.RESPONSE.redirect(location)

        return self._manage_debug(REQUEST)

    #######################################################################
    # Naaya Administration screens
    #######################################################################

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'get_admin_i18n')
    def get_admin_i18n(self):
        """
        Return a wrapper for portal_i18n, providing an interface used
        in rendering admin views and performing admin actions.

        """
        return AdminI18n(self).__of__(self)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_translations_html')
    admin_translations_html = PageTemplateFile('zpt/site_admin_translations', globals())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_messages_html')
    admin_messages_html = PageTemplateFile('zpt/site_admin_messages', globals())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importexport_html')
    admin_importexport_html = PageTemplateFile('zpt/site_admin_importexport', globals())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_editmessage')
    def admin_editmessage(self, message, language, translation, start, skey, rkey, query, REQUEST=None):
        """ """
        ob = self.get_message_catalog()
        ob.edit_message(message_decode(message), language, translation)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_messages_html?msg=%s&start=%s&skey=%s&rkey=%s&query=%s&trans_lang=%s&saved=True' % \
                (self.absolute_url(), quote(message), start, skey, rkey, query, language))

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_delmesg_html')
    admin_delmesg_html = PageTemplateFile('zpt/site_admin_delmessages', globals())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_delmsg')
    def admin_delmsg(self, messages=[], REQUEST=None):
        """ """
        message_catalog = self.get_message_catalog()
        messages = self.utConvertToList(messages)
        for message in messages:
            message_catalog.del_message(message)
        if REQUEST:
            self.getSite().setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_delmesg_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_basket_translations_html')
    admin_basket_translations_html = PageTemplateFile('zpt/site_admin_basket_translations', globals())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_exportmessages')
    def admin_exportmessages(self, x, REQUEST=None, RESPONSE=None):
        """ """
        return self.manage_export_po(x, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importmessages')
    def admin_importmessages(self, lang, file, REQUEST=None, RESPONSE=None):
        """ """
        if REQUEST:
            if not file:
                self.getSite().setSessionErrorsTrans('You must select a file to import.')
                return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())
            else:
                self.manage_import_po(file, lang, REQUEST, RESPONSE)
                self.getSite().setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                return REQUEST.RESPONSE.redirect('%s/admin_translations_html' % self.absolute_url())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_exportxliff')
    def admin_exportxliff(self, x, export_all=1, REQUEST=None, RESPONSE=None):
        """ """
        return self.manage_export_xliff(export_all, x, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'admin_importxliff')
    def admin_importxliff(self, file, REQUEST=None):
        """ """
        raise NotImplementedError("Imports not yet implemented in naaya.i18n")
        if REQUEST:
            if not file:
                self.getSite().setSessionErrorsTrans('You must select a file to import.')
                return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())
            else:
                self.manage_xliff_import(file)
                self.getSite().setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                return REQUEST.RESPONSE.redirect('%s/admin_translations_html' % self.absolute_url())

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'spreadsheet_export')
    def spreadsheet_export(self, target_lang, dialect, REQUEST, RESPONSE):
        """ """
        cat = self.get_message_catalog()
        export_tool = self.get_importexport_tool()
        (headers, content) = export_tool.spreadsheet_export(target_lang, dialect)
        for (header_key, header_value) in headers:
            RESPONSE.setHeader(header_key, header_value)
        return content

    security.declareProtected(PERMISSION_TRANSLATE_PAGES, 'spreadsheet_import')
    def spreadsheet_import(self, file, target_lang, dialect, REQUEST, RESPONSE):
        """ """
        if not file:
            self.setSessionErrorsTrans('You must select a file to import.')
            return RESPONSE.redirect('%s/admin_importexport_html' %
                                     self.absolute_url())
        cat = self.get_message_catalog()
        export_tool = self.get_importexport_tool()
        try:
            export_tool.spreadsheet_import(file, target_lang, dialect)
            self.setSessionInfoTrans('Translations successfully imported.')
        except KeyError, e:
            self.setSessionErrorsTrans('File format does not match selected format.')
        except UnicodeDecodeError, e:
            self.setSessionErrorsTrans('File needs to be utf-8 encoded.')
        except Exception, e:
            self.setSessionErrorsTrans('Error importing translations.')

        return REQUEST.RESPONSE.redirect('%s/admin_importexport_html' % self.absolute_url())

InitializeClass(NaayaI18n)
