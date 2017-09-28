"""
Handle dynamic properties for a specific object

..deprecated:: 2.11.03
    DynamicPropertiesTool is no longer supported.
    This module will be removed in the future version.

"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from naaya.i18n.LocalPropertyManager import (
                                    LocalPropertyManager, LocalProperty)

module_glossary_metatype = "Naaya Glossary"

try:
    from Products.NaayaThesaurus.constants import NAAYATHESAURUS_METATYPE
    module_thesaurus_metatype = NAAYATHESAURUS_METATYPE
except:
    module_thesaurus_metatype = None

class NyProperties(LocalPropertyManager):
    """ This class is exteded by most content types and it is used to manage
    dynamic properties for a specific object.

    """

    def __init__(self):
        """ """

        self.__dynamic_properties = {}

    security = ClassSecurityInfo()

    security.declarePrivate('createProperty')
    def createProperty(self, p_id, p_value, lang):
        """ Add a new property"""

        self.__dynamic_properties[p_id] = ''
        setattr(self, p_id, LocalProperty(p_id))
        self._setLocalPropValue(p_id, lang, p_value)
        self._p_changed = 1

    security.declarePrivate('deleteProperty')
    def deleteProperty(self, p_id):
        """ Delete a property"""

        try:
            del(self.__dynamic_properties[p_id])
            delattr(self, p_id)
            self._p_changed = 1
        except:
            pass

    def getPropertyValue(self, p_id, lang=None):
        """ Returns a property value in the specified language"""

        if lang is None: lang = self.gl_get_selected_language()
        return self.getLocalProperty(p_id, lang)

    def setProperties(self, dict):
        """ A set of properties is stored as a dictionary. this function adds
        properties to the current object

        """

        self.__dynamic_properties = dict
        self._p_changed = 1

    def getProperties(self):
        """ Returns all the properties """
        return self.__dynamic_properties

    security.declarePrivate('createDynamicProperties')
    def createDynamicProperties(self, p_dp_dict, lang):
        """ Create properties with values from a `dict`"""
        for l_dp in p_dp_dict.keys():
            self.createProperty(l_dp, p_dp_dict.get(l_dp, ''), lang)

    security.declarePrivate('updateDynamicProperties')
    def updateDynamicProperties(self, p_dp_dict, lang):
        """ Update properties with values from a `dict`"""
        if lang is None:
            lang = self.gl_get_selected_language()
        for l_dp in p_dp_dict.keys():
            self.createProperty(l_dp, p_dp_dict.get(l_dp, ''), lang)

    security.declarePrivate('updatePropertiesFromGlossary')
    def updatePropertiesFromGlossary(self, lang):
        """ Update the `keywords` and `coverage` properties from the associated
        glossary for each language other than the current one

        """

        provider_keywords = self.get_keywords_glossary()
        if provider_keywords:
            update_translation(self, 'keywords', provider_keywords, lang, '')
        provider_coverage = self.get_coverage_glossary()
        if provider_coverage:
            update_translation(self, 'coverage', provider_coverage, lang, '')

InitializeClass(NyProperties)

def languages_map(ctx):
    lang_names = {}
    for lang_info in ctx.gl_get_languages_mapping():
        lang_names[lang_info['code']] = lang_info['name']
    return lang_names

def _translate_to_langs(source_values, translator, lang, lang_names):
    res = dict((target_lang, [])
               for target_lang in lang_names
               if target_lang != lang)

    #search associated translations from glossary
    if translator.meta_type == module_glossary_metatype:
        for v in source_values:
            gloss_elems = translator.searchGlossary(query=v,
                                                    language=lang_names[lang],
                                                    definition='')

            #search for the exact match
            exact_elem = None
            for l_elem in gloss_elems[2]:
                l_trans = l_elem.get_translation_by_language(lang_names[lang])
                if l_trans.strip() == v.strip():
                    exact_elem = l_elem
                    break

            #get the translations of the exact match
            if exact_elem:
                for target_lang in res:
                    trans = exact_elem.get_translation_by_language(lang_names[target_lang])
                    if trans:
                        res[target_lang].append(trans)

    #search associated translations from thesaurus
    elif translator.meta_type == module_thesaurus_metatype:
        for v in source_values:
            th_term = translator.searchThesaurusNames(query=v, lang=lang)

            #search for the exact match
            exact_term = None
            for k in th_term:
                l_term = translator.getTermByID(k.concept_id, lang)
                if l_term.concept_name.strip() == v.strip():
                    exact_term = l_term
                    break

            #get the translations of the exact match
            if exact_term:
                for target_lang in res:
                    exact_term = translator.getTermByID(exact_term.concept_id,
                                                        target_lang)
                    if exact_term:
                        trans = exact_term.concept_name
                        if trans:
                            res[target_lang].append(trans)

    return res

def update_translation(ob, name, translator, lang, old_value, separator=','):
    """ Updates the given property for all languages. """

    lang_names = languages_map(ob)

    prev_translated = _translate_to_langs(ob.splitToList(old_value),
                                          translator, lang, lang_names)

    new_value = ob.getLocalProperty(name, lang)
    new_translated = _translate_to_langs(ob.splitToList(new_value),
                                         translator, lang, lang_names)

    #set values
    for target_lang in new_translated:
        prev_items = prev_translated[target_lang]

        prev_target_value = ob.getLocalProperty(name, target_lang)
        new_items = [s.strip()
                     for s in ob.splitToList(prev_target_value, separator)
                     if s.strip()]

        for item in list(new_items):
            if item in prev_items:
                new_items.remove(item)

        for item in new_translated[target_lang]:
            if item not in new_items:
                new_items.append(item)

        if not separator.endswith(' '):
            separator += ' '
        new_value = separator.join(new_items)
        ob._setLocalPropValue(name, target_lang, new_value)
