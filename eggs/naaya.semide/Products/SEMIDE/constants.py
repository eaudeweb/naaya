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
# Alexandru Ghica, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports

#Product imports
import Globals


#portal related
SEMIDE_PRODUCT_NAME =       'SEMIDE'
SEMIDE_PRODUCT_PATH =       Globals.package_home(globals())

PERMISSION_ADD_SEMIDESITE = 'SEMIDE - Add SEMIDE Site objects'

METATYPE_SEMIDESITE =       'SEMIDE Site'

#interface related
MESSAGE_EMAILSENT =         'Email sent to all subscribers'
MESSAGE_GENERATED =          'Message generated succesfully'

#content related
ID_LINKCHECKER =        'LinkChecker'
TITLE_LINKCHECKER =     'Link checker'

ID_RDFCALENDAR =        'portal_rdfcalendar'
TITLE_RDFCALENDAR =     'RDF Calendar'

ID_LINKCHECKER =        'portal_linkchecker'
TITLE_LINKCHECKER =     'Link checker'

ID_PHOTOARCHIVE =       'photos'
TITLE_PHOTOARCHIVE =    'Photos'

ID_FLASHTOOL =          'FlashTool'
TITLE_FLASHTOOL =       'Flash builder'
FLASHTOOL_METATYPE =    'SEMIDE Flash Tool'

FLASHTEMPLATE_METATYPE =  'FlashTemplate'
FLASHCATEGORY_METATYPE =  'FlashCategory'

ID_XSLTEMPLATE =      'XSLTemplate'
TITLE_XSLTEMPLATE =   'XSLT template'
XSLTEMPLATE_METATYPE =  'XSLTemplate'

#thesaurus related
ID_THESAURUS =          'portal_thesaurus'
TITLE_THESAURUS =       'SEMIDE thesaurus'

#glossaries related
ID_GLOSSARY_COVERAGE = 'glossary_coverage'
TITLE_GLOSSARY_COVERAGE = 'Coverage glossary'

ID_GLOSSARY_LANGUAGES = 'glossary_languages'
TITLE_GLOSSARY_LANGUAGES = 'Languages glossary'

ID_GLOSSARY_RIVER_BASIN = 'glossary_river_basin'
TITLE_GLOSSARY_RIVER_BASIN = 'River basin glossary'

#calendar related
ID_CALENDAR =           'portal_calendar'
ID_CALENDAR_CSS =       'calendar_style'
ID_RIGHT_ARROW =        'right_arrow'
ID_LEFT_ARROW =         'left_arrow'
CALENDAR_STARTING_DAY = 'Monday'

#flash related
INBRIEF = 'Inbrief'
NOMINATION = 'Nomination'
VACANCIES = 'Vacancies'
CALLFORPROPOSALS = 'Procurement'
TENDERS = 'Call for tenders and proposals'
PAPERS = 'CallForPaper'
TRAINING = 'Training'

#zip download related
ZIP_DOWNLOAD_FILENAME = 'nfp_download.zip'
ZIP_VALID_FILE = 'You must specify a valid file!'
ZIP_CREATED = 'The Documents were successfully created!'
ZIP_HIERARCHICAL = 'The zip file you specified is hierarchical. It contains folders.\nPlease upload a non-hierarchical structure of files.'

#markers
MARKER_TOPMENUCOLOR_START =         '/*s1*/'
MARKER_TOPMENUCOLOR_END =           '/*e1*/'
MARKER_RIGHTPORTLETOUTLINE_START =  '/*s2*/'
MARKER_RIGHTPORTLETOUTLINE_END =    '/*e2*/'

MARKER_ENTIRE_SITE_FONT_START =                  '/*s3*/'
MARKER_ENTIRE_SITE_FONT_END =                    '/*e3*/'
MARKER_ENTIRE_SITE_FONT_AR_START =               '/*s36*/'
MARKER_ENTIRE_SITE_FONT_AR_END =                 '/*e36*/'

MARKER_HEADINGS_FONT_AR_START =                  '/*s37*/'
MARKER_HEADINGS_FONT_AR_END =                    '/*e37*/'
MARKER_HEADINGS_FONT_START =                     '/*s4*/'
MARKER_HEADINGS_FONT_END =                       '/*e4*/'

MARKER_MAIN_NAVIGATION_FONT_START =              '/*s5*/'
MARKER_MAIN_NAVIGATION_FONT_END =                '/*e5*/'
MARKER_MAIN_NAVIGATION_FONT_AR_START =           '/*s38*/'
MARKER_MAIN_NAVIGATION_FONT_AR_END =             '/*e38*/'

MARKER_LEFT_TITLE_FONT_START =                   '/*s6*/'
MARKER_LEFT_TITLE_FONT_END =                     '/*e6*/'
MARKER_LEFT_TITLE_FONT_AR_START =                '/*s39*/'
MARKER_LEFT_TITLE_FONT_AR_END =                  '/*e39*/'

MARKER_LEFT_SECOND_FONT_START =                  '/*s7*/'
MARKER_LEFT_SECOND_FONT_END =                    '/*e7*/'
MARKER_LEFT_SECOND_FONT_AR_START =               '/*s40*/'
MARKER_LEFT_SECOND_FONT_AR_END =                 '/*e40*/'

MARKER_LEFT_THIRD_FONT_START =                   '/*s8*/'
MARKER_LEFT_THIRD_FONT_END =                     '/*e8*/'
MARKER_LEFT_THIRD_FONT_AR_START =                '/*s41*/'
MARKER_LEFT_THIRD_FONT_AR_END =                  '/*e41*/'

MARKER_BREAD_COLOR_START =                       '/*s9*/'
MARKER_BREAD_COLOR_END =                         '/*e9*/'
MARKER_BREAD_SIZE_AR_START =                     '/*s42*/'
MARKER_BREAD_SIZE_AR_END =                       '/*e42*/'
MARKER_BREAD_SIZE_START =                        '/*s10*/'
MARKER_BREAD_SIZE_END =                          '/*e10*/'

MARKER_LEFT_TITLE_BG_START =                     '/*s11*/'
MARKER_LEFT_TITLE_BG_END =                       '/*e11*/'
MARKER_LEFT_TITLE_COLOR_START =                  '/*s12*/'
MARKER_LEFT_TITLE_COLOR_END =                    '/*e12*/'

MARKER_LEFT_ACTIVE_BG_START =                    '/*s13*/'
MARKER_LEFT_ACTIVE_BG_END =                      '/*e13*/'
MARKER_LEFT_ACTIVE_COLOR_START =                 '/*s14*/'
MARKER_LEFT_ACTIVE_COLOR_END =                   '/*e14*/'
MARKER_LEFT_ACTIVE_SIZE_START =                  '/*s15*/'
MARKER_LEFT_ACTIVE_SIZE_END =                    '/*e15*/'

MARKER_RIGHT_BG_START =                          '/*s16*/'
MARKER_RIGHT_BG_END =                            '/*e16*/'
MARKER_RIGHT_TITLE_SIZE_START =                  '/*s17*/'
MARKER_RIGHT_TITLE_SIZE_END =                    '/*e17*/'
MARKER_RIGHT_TITLE_COLOR_START =                 '/*s18*/'
MARKER_RIGHT_TITLE_COLOR_END =                   '/*e18*/'

MARKER_RIGHT_FONT_START =                        '/*s19*/'
MARKER_RIGHT_FONT_END =                          '/*e19*/'
MARKER_RIGHT_FONT_AR_START =                     '/*s43*/'
MARKER_RIGHT_FONT_AR_END =                       '/*e43*/'
MARKER_RIGHT_COLOR_START =                       '/*s20*/'
MARKER_RIGHT_COLOR_END =                         '/*e20*/'
MARKER_RIGHT_SIZE_START =                        '/*s21*/'
MARKER_RIGHT_SIZE_END =                          '/*e21*/'

MARKER_LEFT_TITLE_BORDER_START =                 '/*s22*/'
MARKER_LEFT_TITLE_BORDER_END =                   '/*e22*/'
MARKER_RIGHT_TITLE_FONT_START =                  '/*s23*/'
MARKER_RIGHT_TITLE_FONT_END =                    '/*e23*/'
MARKER_RIGHT_TITLE_FONT_AR_START =               '/*s44*/'
MARKER_RIGHT_TITLE_FONT_AR_END =                 '/*e44*/'


MARKER_SITE_TITLE_FONT_START =                   '/*s24*/'
MARKER_SITE_TITLE_FONT_END =                     '/*e24*/'
MARKER_SITE_TITLE_FONT_AR_START =                '/*s45*/'
MARKER_SITE_TITLE_FONT_AR_END =                  '/*e45*/'


MARKER_BREADBAR_BG_START =                       '/*s25*/'
MARKER_BREADBAR_BG_END =                         '/*e25*/'
MARKER_SEARCH_BG_START =                         '/*s26*/'
MARKER_SEARCH_BG_END =                           '/*e26*/'
MARKER_QUICK_BG_START =                          '/*s27*/'
MARKER_QUICK_BG_END =                            '/*e27*/'


MARKER_QUICK_RIGHT_BORDER_START =                '/*s28*/'
MARKER_QUICK_RIGHT_BORDER_END =                  '/*e28*/'
MARKER_SEARCH_LEFT_BORDER_START =                '/*s49*/'
MARKER_SEARCH_LEFT_BORDER_END =                  '/*e49*/'

MARKER_BREADBAR_MIDDLE_WIDTH_START =             '/*s29*/'
MARKER_BREADBAR_MIDDLE_WIDTH_END =               '/*e29*/'
MARKER_BREADBAR_MIDDLE_BG_START =                '/*s30*/'
MARKER_BREADBAR_MIDDLE_BG_END =                  '/*e30*/'
MARKER_BREADBAR_UPPER_BORDER_START =             '/*s31*/'
MARKER_BREADBAR_UPPER_BORDER_END =               '/*e31*/'
MARKER_BREADBAR_LOWER_BORDER_START =             '/*s32*/'
MARKER_BREADBAR_LOWER_BORDER_END =               '/*e32*/'

MARKER_SEARCH_BGIMG_START =                       '/*s33*/'
MARKER_SEARCH_BGIMG_END =                         '/*e33*/'
MARKER_SEARCH_BGIMG_AR_START =                    '/*s46*/'
MARKER_SEARCH_BGIMG_AR_END =                      '/*e46*/'
MARKER_QUICK_BGIMG_START =                        '/*s34*/'
MARKER_QUICK_BGIMG_END =                          '/*e34*/'
MARKER_QUICK_BGIMG_AR_START =                     '/*s47*/'
MARKER_QUICK_BGIMG_AR_END =                       '/*e47*/'

MARKER_BREADBAR_BGIMG_START =                     '/*s35*/'
MARKER_BREADBAR_BGIMG_END =                       '/*e35*/'
MARKER_BREADBAR_BGIMG_AR_START =                  '/*s48*/'
MARKER_BREADBAR_BGIMG_AR_END =                    '/*e48*/'

RDF_SEARCH_MAPPING = {
    'projects': 'getProjectsListing',
    'news': 'getNewsListing',
    'events': 'getEventsListing',
    'resources': 'getResourceListing',
}

RDF_SEARCH_QUERY_MAPPING = {
    'sq': 'query',
    'mt': 'meta_types',
    'tp': 'textlaws_props',
    'dp': 'document_props',
    'mp': 'multimedia_propes',
    'sd': 'start_date',
    'ed': 'end_date',
    'sl': 'languages',
}
