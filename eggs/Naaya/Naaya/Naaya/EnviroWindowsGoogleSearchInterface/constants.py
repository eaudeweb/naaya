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
#
#
#$Id: constants.py 2719 2004-11-29 17:08:51Z finrocvs $

#Python imports

#Zope imports

#Product imports

#Default ID and TITLE
EWGOOGLEENGINE_ID = 'EWGoogleEngine'
EWGOOGLEENGINE_TITLE = 'EWGoogleEngine'
EWGOOGLESEARCHINTERFACE_ID = 'GoogleSearch'

#Meta types
METATYPE_EWGOOGLEENGINE = 'EWGoogleEngine'
METATYPE_EWGOOGLESEARCHINTERFACE = 'EWGoogleSearchInterface'

#Others
DEFAULT_MAXRESULTS = 10

SESSION_GOOGLE_CACHED_RESULT = 'google_cached_result'

DEFAULT_LANGUAGES_LIST = [
    ('', 'any language'),
    ('lang_ar', 'Arabic'), ('lang_bg', 'Bulgarian'), ('lang_ca', 'Catalan'),
    ('lang_zh-CN', 'Chinese (Simplified)'), ('lang_zh-TW', 'Chinese (Traditional)'), ('lang_hr', 'Croatian'),
    ('lang_cs', 'Czech'), ('lang_da', 'Danish'), ('lang_nl', 'Dutch'),
    ('lang_en', 'English'), ('lang_et', 'Estonian'), ('lang_fi', 'Finnish'),
    ('lang_fr', 'French'), ('lang_de', 'German'), ('lang_el', 'Greek'),
    ('lang_iw', 'Hebrew'), ('lang_hu', 'Hungarian'), ('lang_is', 'Icelandic'),
    ('lang_id', 'Indonesian'), ('lang_it', 'Italian'), ('lang_ja', 'Japanese'),
    ('lang_ko', 'Korean'), ('lang_lv', 'Latvian'), ('lang_lt', 'Lithuanian'),
    ('lang_no', 'Norwegian'), ('lang_pl', 'Polish'), ('lang_pt', 'Portuguese'),
    ('lang_ro', 'Romanian'), ('lang_ru', 'Russian'), ('lang_sr', 'Serbian'),
    ('lang_sk', 'Slovak'), ('lang_sl', 'Slovenian'), ('lang_es', 'Spanish'),
    ('lang_sv', 'Swedish'), ('lang_tr', 'Turkish')
]

DEFAULT_FILETYPES_LIST = [
    ('', 'any format'),
    ('pdf', 'Adobe Acrobat PDF (.pdf)'),
    ('ps', 'Adobe Postscript (.ps)'),
    ('doc', 'Microsoft Word (.doc)'),
    ('xls', 'Microsoft Excel (.xls)'),
    ('ppt', 'Microsoft Powerpoint (.ppt)'),
    ('rtf', 'Rich Text Format (.rtf)')
]

DEFAULT_UPDATEDATES_LIST = [
    ('all', 'anytime'),
    ('m3', 'past 3 months'),
    ('m6', 'past 6 months'),
    ('y', 'past year')
]

DEFAULT_OCCURRENCES_LIST = [
    ('any', 'anywhere in the page'),
    ('title', 'in the title of the page'),
    ('body', 'in the text of the page'),
    ('url', 'in the url of the page'),
    ('links', 'in links to the page')
]

DEFAULT_CONTENTTYPES_DICTIONARY = {
    'application/pdf':'',
    'application/postscript':'',
    'application/msword':'',
    'application/vnd.ms-excel':'',
    'application/vnd.ms-powerpoint':'',
    'application/rtf':''
}
