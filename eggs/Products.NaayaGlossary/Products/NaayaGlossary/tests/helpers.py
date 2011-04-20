from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre

known_languages = {
    'en': "English",
    'de': "German",
    'ru': "Russian",
}

def make_glossary(ctx, id='my_glossary', langs=[]):
    manage_addGlossaryCentre(ctx, id)
    glossary = ctx[id]
    for lang_code in langs:
        add_language(glossary, lang_code, known_languages[lang_code])
    return glossary

def add_folder(parent, id, title, translations={}):
    parent.manage_addGlossaryFolder(id, title)
    ob = parent[id]
    for language, value in translations.iteritems():
        ob.set_translations_list(language, value)
    return ob

def add_element(parent, id, title, translations={}):
    parent.manage_addGlossaryElement(id, title)
    ob = parent[id]
    for language, value in translations.iteritems():
        ob.set_translations_list(language, value)
    return ob

def add_language(glossary, lang, english_name):
    glossary.set_languages_list(lang, english_name)
    glossary.updateObjectsByLang(english_name)

    catalog_obj = glossary.getGlossaryCatalog()
    from ZPublisher.HTTPRequest import record
    index_extra = record()
    index_extra.default_encoding = 'utf-8'
    catalog_obj.manage_addIndex(glossary.cookCatalogIndex(english_name),
                                'TextIndexNG3',index_extra)
