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
This module contains the class that handles dynamic properties for a single.
The I{dynamic properties} are the object properties that can be added and
managed at runtime.
"""

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import PERMISSION_EDIT_OBJECTS
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty

try:
    from Products.NaayaGlossary.constants import NAAYAGLOSSARY_CENTRE_METATYPE
    module_glossary_metatype = NAAYAGLOSSARY_CENTRE_METATYPE
except:
    module_glossary_metatype = None

try:
    from Products.NaayaThesaurus.constants import NAAYATHESAURUS_METATYPE
    module_thesaurus_metatype = NAAYATHESAURUS_METATYPE
except:
    module_thesaurus_metatype = None

class NyProperties(LocalPropertyManager):
    """
    Class that handles dynamic properties for a single.
    """

    manage_options = (
        (
            {'label': 'Dynamic properties', 'action': 'manage_dynamicproperties_html'},
        )
    )

    def __init__(self):
        """ """
        self.__dynamic_properties = {}

    security = ClassSecurityInfo()

    security.declarePrivate('createProperty')
    def createProperty(self, p_id, p_value, lang):
        """
        Add a new property.
        @param p_id: property id
        @type p_id: string
        @param p_value: property value
        @type p_value: unicode
        @param lang: language code
        @type lang: string
        """
        self.__dynamic_properties[p_id] = ''
        setattr(self, p_id, LocalProperty(p_id))
        self._setLocalPropValue(p_id, lang, p_value)
        self._p_changed = 1

    security.declarePrivate('deleteProperty')
    def deleteProperty(self, p_id):
        """
        Delete a property.
        @param p_id: property id
        @type p_id: string
        """
        try:
            del(self.__dynamic_properties[p_id])
            delattr(self, p_id)
            self._p_changed = 1
        except:
            pass

    def getPropertyValue(self, p_id, lang=None):
        """
        Returns a property value in the specified language.
        @param p_id: property id
        @type p_id: string
        @param lang: language code
        @type lang: string
        """
        if lang is None: lang = self.gl_get_selected_language()
        return self.getLocalProperty(p_id, lang)

    def setProperties(self, dict):
        """
        A set of properties is stored as a dictionary. this function adds
        properties to the current object.
        @param dict: structure that holds properties
        @type dict: dictionary
        """
        self.__dynamic_properties = dict
        self._p_changed = 1

    def getProperties(self):
        """
        Returns all the properties.
        """
        return self.__dynamic_properties

    security.declarePrivate('createDynamicProperties')
    def createDynamicProperties(self, p_dp_dict, lang):
        """
        Create properties with values from a given dictionary.
        @param p_dp_dict: structure that holds the properties values
        @type p_dp_dict: dictionary
        @param lang: language code
        @type lang: string
        """
        for l_dp in p_dp_dict.keys():
            self.createProperty(l_dp, p_dp_dict.get(l_dp, ''), lang)

    security.declarePrivate('updateDynamicProperties')
    def updateDynamicProperties(self, p_dp_dict, lang):
        """
        Update properties with values from a given dictionary.
        @param p_dp_dict: structure that holds the properties values
        @type p_dp_dict: dictionary
        @param lang: language code
        @type lang: string
        """
        for l_dp in p_dp_dict.keys():
            self.createProperty(l_dp, p_dp_dict.get(l_dp, ''), lang)

    def __updatePropertyFromGlossary(self, provider, prop, lang_code, lang_name):
        """
        Updates the given property for all languages.
        @param provider: provider object (can be a glossary or a thesaurus)
        @type provider: instance
        @param prop: property name
        @type prop: string
        @param lang_code: current language code
        @type lang_code: string
        @param lang_name: current language name
        @type lang_name: string
        """
        utStrip = self.utStripString
        langs = self.gl_get_languages_mapping()
        res = {}

        #creates the results dictionary
        for l in langs:
            if l['name'] != lang_name:
                res[l['code']] = ''

        #search associated translations from glossary
        if provider.meta_type == module_glossary_metatype:
            for v in self.splitToList(self.getLocalProperty(prop, lang_code)):
                gloss_elems = provider.searchGlossary(query=v, language=lang_name, definition='')

                #search for the exact match
                exact_elem = None
                for l_elem in gloss_elems[2]:
                    l_trans = l_elem.get_translation_by_language(lang_name)
                    if utStrip(l_trans) == utStrip(v):
                        exact_elem = l_elem
                        break

                #get the translations of the exact match
                if exact_elem:
                    for l in langs:
                        l_code = l['code']
                        l_name = l['name']
                        if l_name != lang_name:
                            trans = exact_elem.get_translation_by_language(l_name)
                            if res[l_code] and trans:        res[l_code] = '%s, %s' % (res[l_code], trans)
                            elif not res[l_code] and trans:  res[l_code] = trans

        #search associated translations from thesaurus
        elif provider.meta_type == module_thesaurus_metatype:
            for v in self.splitToList(self.getLocalProperty(prop, lang_code)):
                th_term = provider.searchThesaurusNames(query=v, lang=lang_code)

                #search for the exact match
                exact_term = None
                for k in th_term:
                    l_term = provider.getTermByID(k.concept_id, lang_code)
                    if utStrip(l_term.concept_name) == utStrip(v):
                        exact_term = l_term
                        break

                #get the translations of the exact match
                if exact_term:
                    for l in langs:
                        l_code = l['code']
                        l_name = l['name']
                        if l_name != lang_name:
                            exact_term = provider.getTermByID(exact_term.concept_id, l_code)
                            if exact_term:
                                trans = exact_term.concept_name
                                if res[l_code] and trans:       res[l_code] = '%s, %s' % (res[l_code], trans)
                                elif not res[l_code] and trans: res[l_code] = trans

        #set values
        for k in res.keys():
            trans = self.utToUnicode(res[k])
            if trans: self._setLocalPropValue(prop, k, trans)

    security.declarePrivate('updatePropertiesFromGlossary')
    def updatePropertiesFromGlossary(self, lang):
        """
        Update the B{keywords} and B{coverage} properties from the associated
        glossary for each language other than the current one.
        """
        lang_name = self.gl_get_language_name(lang)
        provider_keywords = self.get_keywords_glossary()
        if provider_keywords:
            self.__updatePropertyFromGlossary(provider_keywords, 'keywords', lang, lang_name)
        provider_coverage = self.get_coverage_glossary()
        if provider_coverage:
            self.__updatePropertyFromGlossary(provider_coverage, 'coverage', lang, lang_name)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_dynamicproperties_html')
    manage_dynamicproperties_html = PageTemplateFile('zpt/manage_dynamicproperties', globals())

InitializeClass(NyProperties)
