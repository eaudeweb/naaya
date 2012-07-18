import logging
from lxml.builder import E
from lxml.etree import tostring
import xlrd
import re
from cStringIO import StringIO
import collections

log = logging.getLogger(__name__)

language_names = {
    'bg': "Bulgarian",
    'cs': "Czech",
    'da': "Danish",
    'de': "German",
    'en': "English",
    'el': "Greek",
    'es': "Spanish",
    'et': "Estonian",
    'fi': "Finnish",
    'fr': "French",
    'fr-BE': "French/Belgium",
    'it': "Italian",
    'lt': "Lithuanian",
    'lv': "Latvian",
    'mk': "Macedonian",
    'nl': "Dutch",
    'nl-BE': "Dutch/Belgium",
    'no': "Norwegian",
    'pl': "Polish",
    'pt': "Portuguese",
    'ro': "Romanian",
    'ru': "Russian",
    'sk': "Slovak",
    'sv': "Swedish",
}
language_codes = dict((v,k) for (k,v) in language_names.iteritems())

class TransName(object):
    def __init__(self, **kwargs):
        self.values = kwargs

    def __str__(self):
        return self.values['en']

    def __setitem__(self, lang, value):
        self.values[lang] = value

    def __getitem__(self, lang):
        return self.values[lang]

class Term(object):
    def __init__(self, name):
        self.name = name

class Folder(Term):
    def __init__(self, name):
        super(Folder, self).__init__(name)
        self.terms = []

    def append(self, term):
        self.terms.append(term)

    def __iter__(self):
        return self.terms.__iter__()

class Glossary(object):
    def __init__(self):
        self.folders = []
        self.description = {}

    def append(self, folder):
        self.folders.append(folder)

    def __iter__(self):
        return self.folders.__iter__()

def val(cell):
    return cell.value.strip()

class TranslationsExtractor(object):
    def __init__(self, row, start, end):
        self.language_of_col = {}
        for c in range(start, end):
            self.language_of_col[c] = val(row[c])

    def __call__(self, row):
        translations = {}
        for col, language in self.language_of_col.iteritems():
            value = val(row[col])
            if value:
                translations[language_codes[language]] = value
        return translations

def _strip_prefix(text, prefix):
    assert text.startswith(prefix)
    return text[len(prefix):]

def _split_english(translations_dict):
    translations_dict_copy = dict(translations_dict)
    del translations_dict_copy['en']
    return translations_dict['en'], translations_dict_copy

def _warn_if_replacements_incomplete(value, dictionary_keys):
    initial = value
    for fragment_en in dictionary_keys:
        value = value.replace(fragment_en, '')
    value = re.sub(r'([^\w\s]+|\b\d+\b)', '', value).strip()
    if value:
        log.warn("Possibly not all strings replaced: %r -> %r", initial, value)

class DescriptionParser(object):
    dictionary = {}

    def __init__(self, first_row, term_trans,
                 get_translations, default_fragments):

        self.value_en = _strip_prefix(val(first_row[2]), 'Relates to: ')

        term_en, term_trans = _split_english(term_trans)
        self.dictionary[term_en] = term_trans
        self.dictionary.update(default_fragments)

        self.get_translations = get_translations

    def handle(self, extra_row):
        fragment_en = val(extra_row[3])
        fragment_translations = self.get_translations(extra_row)
        self.dictionary[fragment_en] = fragment_translations

    def compile_translations(self):
        lang_codes = set(language_codes.values())

        dictionary_keys = self.dictionary.keys()
        dictionary_keys.sort(reverse=True, key=len)
        _warn_if_replacements_incomplete(self.value_en, dictionary_keys)

        _relates_to_en = 'Relates to:'
        out = {'en': _relates_to_en + ' ' + self.value_en}
        for lang_code in language_codes.values():
            relates_to = self.dictionary[_relates_to_en].get(lang_code, '')
            if relates_to:
                relates_to += ' '

            value = self.value_en

            for fragment_en in dictionary_keys:
                if fragment_en not in value:
                    continue
                fragment_trans = self.dictionary[fragment_en]
                try:
                    fragment_trans_value = fragment_trans[lang_code]
                except KeyError:
                    break # we can't translate in this language!
                value = value.replace(fragment_en, fragment_trans_value)

            else:
                # all translations completed
                out[lang_code] = relates_to + value

        return out

def extract_data_from_xls(xls_path):
    wb = xlrd.open_workbook(xls_path)
    sh = wb.sheet_by_index(0)

    HEADING_ROW = 0 # find out the offset constant
    for HEADING_ROW in range(sh.nrows):
        if sh.cell(HEADING_ROW, 2).value == "Description":
            break
    else:
        raise ValueError("Can not find 'Description' cell")

    get_translations = TranslationsExtractor(sh.row(HEADING_ROW), 4, 24)

    default_fragments = []
    for c in range(4, HEADING_ROW):
        row = sh.row(c)
        value_en = val(row[3])
        trans = get_translations(row)
        trans['en'] = value_en
        default_fragments += [(value_en, trans)]

    glossary = Glossary()
    description_parser = None

    glossary.description.update(get_translations(sh.row(2)))
    glossary.description['en'] = val(sh.row(2)[3])

    for n in range(HEADING_ROW+1, sh.nrows):
        row = sh.row(n)
        theme_name = val(row[0])
        term_name = val(row[1])
        description_fragment_en = val(row[3])

        if theme_name:
            values_trans = dict(en=theme_name, **get_translations(row))
            folder = Folder(TransName(**values_trans))
            glossary.append(folder)
            description_target = folder
            description_parser = DescriptionParser(row, values_trans,
                                    get_translations, default_fragments)
            assert not term_name

        elif term_name:
            values_trans = dict(en=term_name, **get_translations(row))
            term = Term(name=TransName(**values_trans))
            folder.append(term)
            description_target = term
            description_parser = DescriptionParser(row, values_trans,
                                    get_translations, default_fragments)

        elif description_fragment_en:
            description_parser.handle(row)

        # should we save the current definition?
        if n < sh.nrows - 1:
            next_row = sh.row(n+1)
        else:
            next_row = None

        if description_parser is None: # nothing to save
            pass
        elif next_row is not None and val(next_row[3]):
            # next line continues the definition; keep going
            pass
        else: # definition is over, let's wrap it up
            values_trans = description_parser.compile_translations()
            description_target.description = TransName(**values_trans)
            description_parser = None

    return glossary

def print_glossary(glossary):
    for folder in glossary:
        print folder.name
        for term in folder:
            print '>> ', term

def id_generator(pattern='%d'):
    n = 0
    while True:
        n += 1
        yield pattern % (n,)

def term_to_xml(term, tag='name'):
    name_xml = getattr(E, tag)({})
    for lang, value in sorted(term.values.iteritems()):
        name_xml.append(E.translation(value, {'lang': lang}))
    return name_xml

def glossary_to_xml(glossary):
    doc_xml = E.glossary()
    folder_ids = id_generator('%02d')
    for folder in glossary:
        folder_id = folder_ids.next()
        folder_xml = E.folder(id=folder_id, title=folder.name['en'])
        folder_xml.extend([
            term_to_xml(folder.name),
            term_to_xml(folder.description, 'definition'),
        ])

        term_ids = id_generator(folder_id + '_%02d')
        for term in folder:
            term_xml = E.element(id=term_ids.next(), title=term.name['en'])
            term_xml.extend([
                term_to_xml(term.name),
                term_to_xml(term.description, 'definition'),
            ])
            folder_xml.append(term_xml)

        doc_xml.append(folder_xml)

    return doc_xml

def get_metadata(glossary):
    return {
        'languages': collections.OrderedDict(sorted(language_names.items())),
        'properties': {
            'parent_anchors': True,
            'description': collections.OrderedDict(sorted(glossary.description.items())),
        },
    }

def ny_glossary_load_languages(ny_glossary):
    for lang_code, language in language_names.iteritems():
        if language not in ny_glossary.get_english_names():
            ny_glossary._add_language(lang_code, language)

def do_import(ny_glossary, xls_path, autocommit=True):
    """
    Start Zope by running "zopectl debug". Assuming you have a Naaya Glossary
    as `ny_glossary` you can run::

        xls_path = '/path/to/glossary-data.xls'

        import chm_terms_from_xls
        chm_terms_from_xls.do_import(ny_glossary, xls_path)
    """

    ny_glossary_load_languages(ny_glossary)
    glossary_xml = tostring(glossary_to_xml(extract_data_from_xls(xls_path)))
    ny_glossary.xml_dump_import(StringIO(glossary_xml))

    if autocommit:
        import transaction
        msg = 'Glossary %r imported data from %r' % (ny_glossary, xls_path)
        transaction.get().note(msg)
        transaction.commit()


def main():
    import sys
    import json
    logging.basicConfig()
    glossary_data = extract_data_from_xls(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == 'metadata':
        print json.dumps(get_metadata(glossary_data), indent=2)
    else:
        xml = glossary_to_xml(glossary_data)
        sys.stdout.write(tostring(xml, pretty_print=True))


if __name__ == '__main__':
    main()
