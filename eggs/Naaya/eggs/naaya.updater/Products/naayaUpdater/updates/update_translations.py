import re

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.naayaUpdater.updates import UpdateScript, PRIORITY


def backslash_unescape(x):
    trans = [('\\"', '"'), ('\\n', '\n'), ('\\r', '\r'), ('\\t', '\t'),
             ('\\\\', '\\')]
    for a, b in trans:
        x = x.replace(a, b)
    return x

def normalize_code(code):
    """
    Normalizes language code case to ISO639 format, eg. 'en_us' becomes 'en-US'

    """
    not_letter = re.compile(r'[^a-z]+', re.IGNORECASE)
    parts = re.sub(not_letter, '-', code.strip()).split('-', 1)
    parts[0] = parts[0].lower()
    if len(parts) > 1:
        return parts[0] + '-' + parts[1].upper()
    else:
        return parts[0]

def read_po(filehandler, overwrite_with_empty=False):
    """
    Imports a po file in the given `lang` language. Requires a `filehandler`
    to the uploaded file.
    Ignores empty translations.

    """
    # Load the data
    BEFORE_HEADER = 0; IN_HEADER = 1; IN_MAPPINGS = 2
    encoding_pat = re.compile(r'charset=([a-z0-9-]*)', re.IGNORECASE)
    msgid_pat = re.compile(r'^msgid[\t\s]+"(.*?)"$', re.IGNORECASE)
    msgstr_pat = re.compile(r'^msgstr[\t\s]+"(.*?)"$', re.IGNORECASE)
    state = BEFORE_HEADER
    encoding = None
    msgid = None
    data = {}

    filehandler.seek(0)
    for cnt, line in enumerate(filehandler):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if state is BEFORE_HEADER:
            if line == 'msgid ""':
                state = IN_HEADER
        elif state is IN_HEADER:
            enc = encoding_pat.search(line)
            if enc is not None:
                encoding = enc.groups()[0]
                if encoding.lower() not in ('utf8', 'utf-8'):
                    raise ValueError("Only import utf-8 encoded files")
                state = IN_MAPPINGS
        elif state is IN_MAPPINGS:
            if encoding is None:
                raise ValueError(("Missing encoding specification in"
                                  " PO headers. "
                                  "Only import utf-8 encoded files"))
            if msgid is not None and line.startswith('msgstr '):
                match = msgstr_pat.search(line)
                if match is None:
                    raise ValueError("Error reading msgstr at line %d", cnt)
                else:
                    msgid = backslash_unescape(msgid).decode(encoding)
                    msgstr = backslash_unescape(match.groups()[0]).decode(encoding)
                    # ignore empty translations
                    if msgstr or overwrite_with_empty:
                        data[msgid] = msgstr
                    msgid = None
            match = msgid_pat.search(line)
            if match is not None:
                msgid = match.groups()[0]
        else:
            raise Error('Undefined state in parsing .po file')

    return data


class UpdateTranslations(UpdateScript):
    """ Imports .po translations file in all selected portals """
    title = 'Update Translations'
    authors = ['Mihnea Simian']
    creation_date = 'Sep 20, 2011'
    priority = PRIORITY['HIGH']
    description = """Updates translation in portals according to a given
    .PO file. Translations are updated and added if neccessary, regardless of
    their previous value.<br /><br />

    Messages in portal that are not present in .PO remain unchanged.
    """


    def _update(self, portal):
        form = self.REQUEST.form # TODO: don't rely on self.REQUEST
        po_file = form['po_file']
        overwrite_with_empty = form.get('overwrite_with_empty')
        lang = normalize_code(form['lang_code'])
        existing_langs = portal.gl_get_languages()
        if lang not in existing_langs:
            self.log.error("`%s` language not found in portal! Import aborted. "
                           "Existing languages are: %r", lang, existing_langs)
            return False

        # Compatibility code
        # naaya.i18n catalog: edit_message(msgid, lang, translation)
        # localizer catalog: message_edit(message, language, translation, note)
        def update_message_localizer(message, language, translation, note):
            catalog.gettext(message)
            catalog.message_edit(message, language, translation, note)

        if hasattr(portal, 'getPortalI18n'):
            catalog = portal.getPortalI18n().get_message_catalog()
            update_message = lambda x, y, z, w: catalog.edit_message(x, y, z)
        else:
            catalog = portal.getPortalTranslations()
            update_message = update_message_localizer

        data = read_po(po_file, overwrite_with_empty)

        for (msgid, msgstr) in data.items():
            update_message(msgid, lang, msgstr, 'PO Update Translations import')
            self.log.info(u"Translation set: '%s' - '%s'", msgid, msgstr)

        self.log.info("%d translations updated", len(data))
        return True


    update_template = PageTemplateFile('zpt/update_translations', globals())
    update_template.default = UpdateScript.update_template
