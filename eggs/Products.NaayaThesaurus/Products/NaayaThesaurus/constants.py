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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Ghica Alexandru, Finsiel Romania


#Zope imports
import Globals


#product name
NAAYATHESAURUS_PRODUCT_NAME =        'Naaya Thesaurus'
NAAYATHESAURUS_PATH =                Globals.package_home(globals())

#permissions
PERMISSION_ADD_NAAYATHESAURUS =      'Add Naaya Thesaurus'

#containers meta types
NAAYATHESAURUS_METATYPE =       'Naaya Thesaurus'
THESAURUSCATALOG_METATYPE =     'Thesaurus catalog'
THEMES_METATYPE =               'Themes folder'
ALTTERMS_METATYPE =             'Allterms folder'
CONCEPT_RELATIONS_METATYPE =    'Concept relations folder'
CONCEPTS_METATYPE =             'Concepts folder'
DEFINITIONS_METATYPE =          'Definitions folder'
SCOPE_NOTES_METATYPE =          'Scope notes folder'
SOURCE_METATYPE =               'Source folder'
TERMS_METATYPE =                'Terms folder'
THEME_RELATION_METATYPE =       'Theme relations folder'

#data meta types
THEME_ITEM_METATYPE =               'Theme'
CONCEPT_ITEM_METATYPE =             'Concept'
TERM_ITEM_METATYPE =                'Term'
ALTTERM_ITEM_METATYPE =             'AltTerm'
SOURCE_ITEM_METATYPE =              'Source'
SCOPE_ITEM_METATYPE =               'Scope'
DEFINITION_ITEM_METATYPE =          'Definition'
CONCEPT_RELATION_ITEM_METATYPE =    'Concept Relation'
THEME_RELATION_ITEM_METATYPE =      'Theme Relation'

#other
NAAYATHESAURUS_CATALOG_TITLE =  'ThesaurusCatalog'
NAAYATHESAURUS_CATALOG_ID =     'catalog'

#default indexez
THESAURUS_INDEXES = {'meta_type'        :'FieldIndex',
                     'langcode'         :'FieldIndex',
                     'theme_id'         :'FieldIndex',
                     'theme_name'       :'TextIndexNG3',
                     'concept_id'       :'FieldIndex',
                     'relation_id'      :'FieldIndex',
                     'relation_type'    :'FieldIndex',
                     'concept_name'     :'TextIndexNG3',
                     'source_id'        :'FieldIndex',
                     'source_name'      :'TextIndexNG3',
                     'alt_name'         :'TextIndexNG3',
                     'scope_note'       :'TextIndexNG3',
                     'definition'       :'TextIndexNG3'}

#relation types
RELATION_TYPES = {'1':'Broader', '2':'Narrower', '3':'Related'}

#unicode character maps
unicode_character_map = {
                         'en':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'en-US':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'ar':[\
    (u"\u0621", u"\u0674", u"\uFE80", u"\u06FD"), \
    (u"\u0622", u"\uFE82", u"\uFE81"), \
    (u"\u0623", u"\uFE84", u"\uFE83"), \
    (u"\u0672", u"\u0672"), \
    (u"\u0671", u"\uFB51", u"\uFB50"), \
    (u"\u0624", u"\uFE86", u"\uFE85"), \
    (u"\u0625", u"\uFE88", u"\uFE87"), \
    (u"\u0673", u"\u0673"), \
    (u"\u0626", u"\uFE8B", u"\uFE8C", u"\uFE8A", u"\uFE89"), \
    (u"\u0627", u"\uFE8E", u"\uFE8D", u"\uFD3C", u"\uFD3D"), \
    (u"\u066E", u"\u066E"), \
    (u"\u0628", u"\uFE91", u"\uFE92", u"\uFE90", u"\uFE8F"), \
    (u"\u067B", u"\uFB54", u"\uFB55", u"\uFB53", u"\uFB52"), \
    (u"\u067E", u"\uFB58", u"\uFB59", u"\uFB57", u"\uFB56"), \
    (u"\u0680", u"\uFB5C", u"\uFB5D", u"\uFB5B", u"\uFB5A"), \
    (u"\u0629", u"\uFE94", u"\uFE93"), \
    (u"\u062A", u"\uFE97", u"\uFE98", u"\uFE96", u"\uFE95"), \
    (u"\u062B", u"\uFE9B", u"\uFE9C", u"\uFE9A", u"\uFE99"), \
    (u"\u0679", u"\uFB68", u"\uFB69", u"\uFB67", u"\uFB66"), \
    (u"\u067A", u"\uFB60", u"\uFB61", u"\uFB5F", u"\uFB5E"), \
    (u"\u067C", u"\u067C"), \
    (u"\u067D", u"\u067D"), \
    (u"\u067F", u"\uFB64", u"\uFB65", u"\uFB63", u"\uFB62"), \
    (u"\u062C", u"\uFE9F", u"\uFEA0", u"\uFE9E", u"\uFE9D"), \
    (u"\u0683", u"\uFB78", u"\uFB79", u"\uFB77", u"\uFB76"), \
    (u"\u0684", u"\uFB74", u"\uFB75", u"\uFB73", u"\uFB72"), \
    (u"\u0686", u"\uFB7C", u"\uFB7D", u"\uFB7B", u"\uFB7A"), \
    (u"\u06BF", u"\u06BF"), \
    (u"\u0687", u"\uFB80", u"\uFB81", u"\uFB7FB", u"\uFB7E"), \
    (u"\u062D", u"\uFEA3", u"\uFEA4", u"\uFEA2", u"\uFEA1"), \
    (u"\u062E", u"\uFEA7", u"\uFEA8", u"\uFEA6", u"\uFEA5"), \
    (u"\u0681", u"\u0681"), \
    (u"\u0682", u"\u0682"), \
    (u"\u0685", u"\u0685"), \
    (u"\u062F", u"\uFEAA", u"\uFEA9"), \
    (u"\u0630", u"\uFEAC", u"\uFEAB"), \
    (u"\u0688", u"\uFB89", u"\uFB88"), \
    (u"\u0631", u"\uFEAE", u"\uFEAD", u"\uFC5C"), \
    (u"\u0632", u"\uFEB0", u"\uFEAF"), \
    (u"\u0691", u"\uFB8D", u"\uFB8C"), \
    (u"\u0698", u"\uFB8B", u"\uFB8A"), \
    (u"\u0633", u"\uFEB3", u"\uFEB4", u"\uFEB2", u"\uFEB1"), \
    (u"\u0634", u"\uFEB7", u"\uFEB8", u"\uFEB6", u"\uFEB5"), \
    (u"\u0635", u"\uFEBB", u"\uFEBC", u"\uFEBA", u"\uFEB9"), \
    (u"\u0636", u"\uFEBF", u"\uFEC0", u"\uFEBE", u"\uFEBD"), \
    (u"\u0637", u"\uFEC3", u"\uFEC4", u"\uFEC2", u"\uFEC1"), \
    (u"\u0638", u"\uFEC7", u"\uFEC8", u"\uFEC6", u"\uFEC5"), \
    (u"\u0639", u"\uFECB", u"\uFECC", u"\uFECA", u"\uFEC9"), \
    (u"\u063A", u"\uFECF", u"\uFED0", u"\uFECE", u"\uFECD"), \
    (u"\u0641", u"\uFED3", u"\uFED4", u"\uFED2", u"\uFED1"), \
    (u"\u06A4", u"\uFB6C", u"\uFB6D", u"\uFB6B", u"\uFB6A"), \
    (u"\u06A6", u"\uFB70", u"\uFB71", u"\uFB6F", u"\uFB6E"), \
    (u"\u0642", u"\uFED7", u"\uFED8", u"\uFED6", u"\uFED5"), \
    (u"\u0643", u"\uFEDB", u"\uFEDC", u"\uFEDA", u"\uFED9"), \
    (u"\u06A9", u"\uFB90", u"\uFB91", u"\uFB8F", u"\uFB8E"), \
    (u"\u06AD", u"\uFBD5", u"\uFBD6", u"\uFBD4", u"\uFBD3"), \
    (u"\u06AF", u"\uFB94", u"\uFB95", u"\uFB93", u"\uFB92"), \
    (u"\u06B1", u"\uFB9C", u"\uFB9D", u"\uFB9B", u"\uFB9A"), \
    (u"\u06B3", u"\uFB98", u"\uFB99", u"\uFB97", u"\uFB96"), \
    (u"\u0644", u"\uFEDF", u"\uFEE0", u"\uFEDE", u"\uFEDD"), \
    (u"\u0645", u"\uFEE3", u"\uFEE4", u"\uFEE2", u"\uFEE1"), \
    (u"\u0646", u"\uFEE7", u"\uFEE8", u"\uFEE6", u"\uFEE5"), \
    (u"\u0647", u"\uFEEB", u"\uFEEC", u"\uFEEA", u"\uFEE9"), \
    (u"\u0648", u"\u06E5", u"\uFEEE", u"\uFEED"), \
    (u"\u0649", u"\uFBE8", u"\uFBE9", u"\uFEF0", u"\uFEEF"), \
    (u"\u064A", u"\u06E6", u"\uFEF3", u"\uFEF4", u"\uFEF2", u"\uFEF1"), \
    (u"\u06CC", u"\uFBFE", u"\uFBFF", u"\uFBFD", u"\uFBFC")], \
                         'el':[\
    (u"\u03B1", u"\u0391", u"\u03AC", u"\u0386"), \
    (u"\u03B2", u"\u0392"), \
    (u"\u03B3", u"\u0393"), \
    (u"\u03B4", u"\u0394"), \
    (u"\u03B5", u"\u0395", u"\u03AD", u"\u0388"), \
    (u"\u03B6", u"\u0396"), \
    (u"\u03B7", u"\u0397", u"\u03AE", u"\u0389"), \
    (u"\u03B8", u"\u0398"), \
    (u"\u03B9", u"\u0399", u"\u03AF", u"\u038A", u"\u03CA", u"\u03AA", u"\u0390"), \
    (u"\u03BA", u"\u039A"), \
    (u"\u03BB", u"\u039B"), \
    (u"\u03BC", u"\u039C", u"\u00B5"), \
    (u"\u03BD", u"\u039D"), \
    (u"\u03BE", u"\u039E"), \
    (u"\u03BF", u"\u039F", u"\u03CC", u"\u038C"), \
    (u"\u03C0", u"\u03A0"), \
    (u"\u03C1", u"\u03A1"), \
    (u"\u03C3", u"\u03A3", u"\u03C2"), \
    (u"\u03C4", u"\u03A4"), \
    (u"\u03C5", u"\u03A5", u"\u03CD", u"\u038E", u"\u03CB", u"\u03AB", u"\u03B0"), \
    (u"\u03C6", u"\u03A6"), \
    (u"\u03C7", u"\u03A7"), \
    (u"\u03C8", u"\u03A8"), \
    (u"\u03C9", u"\u03A9", u"\u2126", u"\u03CE", u"\u038F")], \
                         'bg':[\
    (u"\u0430", u"\u0410"), \
    (u"\u0431", u"\u0411"), \
    (u"\u0432", u"\u0412"), \
    (u"\u0433", u"\u0413", u"\u0491", u"\u0490"), \
    (u"\u0434", u"\u0414"), \
    (u"\u0435", u"\u0415", u"\u0450", u"\u0400", u"\u0451", u"\u0401"), \
    (u"\u0436", u"\u0416", u"\u04C2", u"\u04C1"), \
    (u"\u0437", u"\u0417"), \
    (u"\u0438", u"\u0418", u"\u045D", u"\u040D", u"\u04E3", u"\u04E2"), \
    (u"\u0439", u"\u0419"), \
    (u"\u043A", u"\u041A"), \
    (u"\u043B", u"\u041B"), \
    (u"\u043C", u"\u041C"), \
    (u"\u043D", u"\u041D"), \
    (u"\u043E", u"\u041E"), \
    (u"\u043F", u"\u041F"), \
    (u"\u0440", u"\u0420"), \
    (u"\u0441", u"\u0421"), \
    (u"\u0442", u"\u0422"), \
    (u"\u0443", u"\u0423", u"\u04EF", u"\u04EE"), \
    (u"\u0444", u"\u0424"), \
    (u"\u0445", u"\u0425"), \
    (u"\u0446", u"\u0426"), \
    (u"\u0447", u"\u0427"), \
    (u"\u0448", u"\u0428"), \
    (u"\u0449", u"\u0429"), \
    (u"\u044A", u"\u042A"), \
    (u"\u044C", u"\u042C"), \
    (u"\u044E", u"\u042E"), \
    (u"\u044F", u"\u042F") ],\
                         'da':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A"), \
    (u"\u00E6", u"\u00C6"), \
    (u"\u00F8", u"\u00D8"), \
    (u"\u00E5", u"\u00C5") ],\
                         'et':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0161", u"\u0160"), \
    (u"\u007A", u"\u005A"), \
    (u"\u017E", u"\u017D"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u00F5", u"\u00D5"), \
    (u"\u00E4", u"\u00C4"), \
    (u"\u00F6", u"\u00D6"), \
    (u"\u00FC", u"\u00DC"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059") ],\
                         'fi':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A"), \
    (u"\u00E5", u"\u00C5"), \
    (u"\u00E4", u"\u00C4"), \
    (u"\u00F6", u"\u00D6") ],\
                         'hu':[\
    (u"\u0061", u"\u0041"), \
    (u"\u00E1", u"\u00C1"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0063\u0073", u"\u0043\u0073"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0064\u007A", u"\u0044\u007A", u"\u0044\u005A"), \
    (u"\u0064\u007A\u0073", u"\u0044\u007A\u0073", u"\u0044\u005A\u0053"), \
    (u"\u0065", u"\u0045"), \
    (u"\u00E9", u"\u00C9"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0067\u0079", u"\u0047\u0079", u"\u0047\u0059"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u00ED", u"\u00CD"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006C\u0079", u"\u004C\u0079", u"\u004C\u0059"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006E\u0079", u"\u004E\u0079", u"\u004E\u0059"), \
    (u"\u006F", u"\u004F"), \
    (u"\u00F3", u"\u00D3"), \
    (u"\u00F6", u"\u00D6"), \
    (u"\u0151", u"\u0150"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0073\u007A", u"\u0053\u007A", u"\u0053\u005A"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0074\u0079", u"\u0054\u0079", u"\u0054\u0059"), \
    (u"\u0075", u"\u0055"), \
    (u"\u00FA", u"\u00DA"), \
    (u"\u00FC", u"\u00DC"), \
    (u"\u0171", u"\u0170"), \
    (u"\u0076", u"\u0056"), \
    (u"\u007A", u"\u005A"), \
    (u"\u007A\u0073", u"\u005A\u0073", u"\u005A\u0053") ],\
                         'ru':[\
    (u"\u0430", u"\u0410"), \
    (u"\u0431", u"\u0411"), \
    (u"\u0432", u"\u0412"), \
    (u"\u0433", u"\u0413"), \
    (u"\u0434", u"\u0414"), \
    (u"\u0435", u"\u0415"), \
    (u"\u0451", u"\u0401"), \
    (u"\u0436", u"\u0416"), \
    (u"\u0437", u"\u0417"), \
    (u"\u0438", u"\u0418"), \
    (u"\u0439", u"\u0419"), \
    (u"\u043A", u"\u041A"), \
    (u"\u043B", u"\u041B"), \
    (u"\u043C", u"\u041C"), \
    (u"\u043D", u"\u041D"), \
    (u"\u043E", u"\u041E"), \
    (u"\u043F", u"\u041F"), \
    (u"\u0440", u"\u0420"), \
    (u"\u0441", u"\u0421"), \
    (u"\u0442", u"\u0422"), \
    (u"\u0443", u"\u0423"), \
    (u"\u0444", u"\u0424"), \
    (u"\u0445", u"\u0425"), \
    (u"\u0446", u"\u0426"), \
    (u"\u0447", u"\u0427"), \
    (u"\u0448", u"\u0428"), \
    (u"\u0449", u"\u0429"), \
    (u"\u044A", u"\u042A"), \
    (u"\u044B", u"\u042B"), \
    (u"\u044C", u"\u042C"), \
    (u"\u044D", u"\u042D"), \
    (u"\u044E", u"\u042E"), \
    (u"\u044F", u"\u042F") ],\
                         'eu':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006C\u006C", u"\u004C\u006C", u"\u004C\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u00F1", u"\u00D1"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0072\u0072", u"\u0052\u0072", u"\u0052\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0074\u0073", u"\u0054\u0073", u"\u0054\u0053"), \
    (u"\u0074\u0078", u"\u0054\u0078", u"\u0054\u0058"), \
    (u"\u0074\u007A", u"\u0054\u007A", u"\u0054\u005A"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'cs':[\
    (u"\u0061", u"\u0041"), \
    (u"\u00E1", u"\u00C1"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u010D", u"\u010C"), \
    (u"\u0064", u"\u0044"), \
    (u"\u010F", u"\u010E"), \
    (u"\u0065", u"\u0045"), \
    (u"\u00E9", u"\u00C9"), \
    (u"\u011B", u"\u011A"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0063\u0068", u"\u0043\u0068", u"\u0043\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u00ED", u"\u00CD"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u0148", u"\u0147"), \
    (u"\u006F", u"\u004F"), \
    (u"\u00F3", u"\u00D3"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0159", u"\u0158"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0161", u"\u0160"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0165", u"\u0164"), \
    (u"\u0075", u"\u0055"), \
    (u"\u00FA", u"\u00DA"), \
    (u"\u016F", u"\u016E"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u00FD", u"\u00DD"), \
    (u"\u007A", u"\u005A"), \
    (u"\u017E", u"\u017D") ], \
                         'fr':[\
    (u"\u0061", u"\u0041", u"\u00E0", u"\u00C0", u"\u00E2", u"\u00C2"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043", u"\u00E7", u"\u00C7"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045", u"\u00E9", u"\u00C9", u"\u00E8", u"\u00C8", u"\u00EA", u"\u00CA", u"\u00EB", u"\u00CB"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049", u"\u00EE", u"\u00CE"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F", u"\u00F4", u"\u00D4", u"\u0153", u"\u0152"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055", u"\u00F9", u"\u00D9", u"\u00FB", u"\u00DB"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'it':[\
    (u"\u0061", u"\u0041", u"\u00E0", u"\u00C0"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045", u"\u00E9", u"\u00C9", u"\u00E8", u"\u00C8"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049", u"\u00ED", u"\u00CD", u"\u00EC", u"\u00CC"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F", u"\u00F3", u"\u00D3", u"\u00F2", u"\u00D2"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055", u"\u00FA", u"\u00DA", u"\u00F9", u"\u00D9"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'de':[\
    (u"\u0061", u"\u0041", u"\u00E4", u"\u00C4"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F", u"\u00F6", u"\u00D6"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053", u"\u00DF"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055", u"\u00FC", u"\u00DC"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'pt':[\
    (u"\u0061", u"\u0041", u"\u00E1", u"\u00C1", u"\u00E0", u"\u00C0", u"\u00E2", u"\u00C2", u"\u00E3", u"\u00C3"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043", u"\u00E7", u"\u00C7"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045", u"\u00E9", u"\u00C9", u"\u00EA", u"\u00CA"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049", u"\u00ED", u"\u00CD"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F", u"\u00F3", u"\u00D3", u"\u00F4", u"\u00D4", u"\u00F5", u"\u00D5"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055", u"\u00FA", u"\u00DA"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'es':[\
    (u"\u0061", u"\u0041", u"\u00E1", u"\u00C1"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045", u"\u00E9", u"\u00C9"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049", u"\u00ED", u"\u00CD"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u00F1", u"\u00D1"), \
    (u"\u006F", u"\u004F", u"\u00F3", u"\u00D3"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055", u"\u00FA", u"\u00DA"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A") ],\
                         'nl':[\
    (u"\u0061", u"\u0041", u"\u00E4", u"\u00C4"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045", u"\u00EB", u"\u00CB"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049", u"\u00EF", u"\u00CF"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F", u"\u00F6", u"\u00D6"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055", u"\u00FC", u"\u00DC"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u0133", u"\u0132"), \
    (u"\u007A", u"\u005A") ],\
                         'no':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A"), \
    (u"\u00E6", u"\u00C6"), \
    (u"\u00F8", u"\u00D8"), \
    (u"\u00E5", u"\u00C5") ],\
                         'pl':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0105", u"\u0104"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0107", u"\u0106"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0119", u"\u0118"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u0142", u"\u0141"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u0144", u"\u0143"), \
    (u"\u006F", u"\u004F"), \
    (u"\u00F3", u"\u00D3"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u015B", u"\u015A"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A"), \
    (u"\u017A", u"\u0179"), \
    (u"\u017C", u"\u017B") ],\
                         'sk':[\
    (u"\u0061", u"\u0041"), \
    (u"\u00E1", u"\u00C1"), \
    (u"\u00E4", u"\u00C4"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u010D", u"\u010C"), \
    (u"\u0064", u"\u0044"), \
    (u"\u010F", u"\u010E"), \
    (u"\u0064\u007A", u"\u0044\u007A", u"\u0044\u005A"), \
    (u"\u0064\u017E", u"\u0044\u017E", u"\u0044\u017D"), \
    (u"\u0065", u"\u0045"), \
    (u"\u00E9", u"\u00C9"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0063\u0068", u"\u0043\u0068", u"\u0043\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u00ED", u"\u00CD"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u013A", u"\u0139"), \
    (u"\u013E", u"\u013D"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u0148", u"\u0147"), \
    (u"\u006F", u"\u004F"), \
    (u"\u00F3", u"\u00D3"), \
    (u"\u00F4", u"\u00D4"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0155", u"\u0154"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0161", u"\u0160"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0165", u"\u0164"), \
    (u"\u0075", u"\u0055"), \
    (u"\u00FA", u"\u00DA"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u00FD", u"\u00DD"), \
    (u"\u007A", u"\u005A"), \
    (u"\u017E", u"\u017D") ],\
                         'sl':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u010D", u"\u010C"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0161", u"\u0160"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A"), \
    (u"\u017E", u"\u017D") ],\
                         'sv':[\
    (u"\u0061", u"\u0041"), \
    (u"\u0062", u"\u0042"), \
    (u"\u0063", u"\u0043"), \
    (u"\u0064", u"\u0044"), \
    (u"\u0065", u"\u0045"), \
    (u"\u0066", u"\u0046"), \
    (u"\u0067", u"\u0047"), \
    (u"\u0068", u"\u0048"), \
    (u"\u0069", u"\u0049"), \
    (u"\u006A", u"\u004A"), \
    (u"\u006B", u"\u004B"), \
    (u"\u006C", u"\u004C"), \
    (u"\u006D", u"\u004D"), \
    (u"\u006E", u"\u004E"), \
    (u"\u006F", u"\u004F"), \
    (u"\u0070", u"\u0050"), \
    (u"\u0071", u"\u0051"), \
    (u"\u0072", u"\u0052"), \
    (u"\u0073", u"\u0053"), \
    (u"\u0074", u"\u0054"), \
    (u"\u0075", u"\u0055"), \
    (u"\u0076", u"\u0056"), \
    (u"\u0077", u"\u0057"), \
    (u"\u0078", u"\u0058"), \
    (u"\u0079", u"\u0059"), \
    (u"\u007A", u"\u005A"), \
    (u"\u00E5", u"\u00C5"), \
    (u"\u00E4", u"\u00C4"), \
    (u"\u00F6", u"\u00D6") ]\
    }
