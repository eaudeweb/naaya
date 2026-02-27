"""
Load translations from the hand-edited Excel file into a glossary. Intended
usage:

  * copy/symlink this file to somewhere so it can be imported
  * start up a Zope instance with the "debug" command, to get an interactive
    interpreter
  * run the following::

        from load_glossary_from_excel improt magic
        magic(app['chm-site']['chm_terms'], "/path/to/excel/file.xls")
"""

from lxml.builder import E
from lxml.etree import tostring
import xlrd

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
    'it': "Italian",
    'lt': "Lithuanian",
    'lv': "Latvian",
    'nl': "Dutch",
    'no': "Norwegian",
    'pl': "Polish",
    'pt': "Portuguese",
    'ro': "Romanian",
    'ru': "Russian",
    'sk': "Slovak",
    'sv': "Swedish",
}
language_codes = dict((v,k) for (k,v) in language_names.iteritems())

class Name(object):
    def __init__(self, **kwargs):
        self.values = kwargs

    def __str__(self):
        return self.values['en']

    def __setitem__(self, lang, value):
        self.values[lang] = value

class NameList(object):
    def __init__(self, name):
        self.name = name
        self.terms = []

    def append(self, term):
        self.terms.append(term)

    def __iter__(self):
        return self.terms.__iter__()

class Glossary(object):
    def __init__(self):
        self.themes = []

    def append(self, theme):
        self.themes.append(theme)

    def __iter__(self):
        return self.themes.__iter__()

def print_glossary(glossary):
    for theme in glossary:
        print theme.name
        for term in theme:
            print '>> ', term

def name_to_xml(the_name, tag='name'):
    name_xml = E.name({})
    for lang, value in the_name.values.iteritems():
        name_xml.append(E.translation(value, {'lang': lang}))
    return name_xml

def glossary_to_xml(glossary):
    doc_xml = E.glossary()
    for theme in glossary:
        theme_xml = E.theme(name_to_xml(theme.name))
        doc_xml.append(theme_xml)
        for term in theme:
            term_xml = E.term(name_to_xml(term))
            theme_xml.append(term_xml)

    return doc_xml

def extract_skos_from_xls(xls_path):
    wb = xlrd.open_workbook(xls_path)
    sh = wb.sheet_by_index(0)

    HEADING_ROW = 8
    assert sh.cell(HEADING_ROW, 2).value == "Description"

    language_of_col = {}
    for c in range(4, 24):
        language_of_col[c] = sh.cell(HEADING_ROW, c).value

    def translations(row):
        for col, language in language_of_col.iteritems():
            value = sh.cell(row, col).value.strip()
            if value:
                yield language_codes[language], value

    glossary = Glossary()
    for row in range(HEADING_ROW+1, sh.nrows):
        theme_name = sh.cell(row, 0).value.strip()
        term_name = sh.cell(row, 1).value.strip()
        if theme_name:
            theme = NameList(Name(en=theme_name, **dict(translations(row))))
            glossary.append(theme)
            assert not term_name
        elif term_name:
            theme.append(Name(en=term_name, **dict(translations(row))))

    #print tostring(glossary_to_xml(glossary), pretty_print=True)
    return glossary

def import_to_ny_glossary(ny_glossary, glossary_data):
    def new_id_generator():
        n = 0
        while True:
            n += 1
            yield n
    folder_id_generator = new_id_generator()

    def translate(ob, translations):
        for lang_code, value in translations.iteritems():
            language = language_names[lang_code]
            ob.set_translations_list(language, value)

    for n, th in enumerate(glossary_data.themes):
        theme_id = '%02d' % folder_id_generator.next()
        title = th.name.values['en']
        #print theme_id, title
        ny_glossary.manage_addGlossaryFolder(theme_id, title)
        ny_glossary_theme = ny_glossary[theme_id]
        translate(ny_glossary_theme, th.name.values)
        element_id_generator = new_id_generator()

        for elem in th:
            element_id = '%s_%02d' % (theme_id, element_id_generator.next())
            title = elem.values['en']
            #print element_id, title
            ny_glossary_theme.manage_addGlossaryElement(element_id, title)
            ny_glossary_element = ny_glossary_theme[element_id]
            translate(ny_glossary_element, elem.values)

def import_languages(ny_glossary):
    for lang_code, language in language_names.iteritems():
        if language not in ny_glossary.get_english_names():
            #print 'Adding language %s (%s)' % (language, lang_code)
            ny_glossary._add_language(lang_code, language)

def magic(ny_glossary, xls_path):
    glossary_data = extract_skos_from_xls(xls_path)
    #print tostring(glossary_to_xml(glossary_data), pretty_print=True)

    import_languages(ny_glossary)
    import_to_ny_glossary(ny_glossary, glossary_data)

    import transaction
    transaction.get().note("Import glossary data from %r" % xls_path)
    transaction.commit()

def main():
    import sys
    xls_path = sys.argv[1]
    extract_skos_from_xls(xls_path)

if __name__ == '__main__':
    main()
