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
try:
    from App.ImageFile import ImageFile
except:
    from App.ImageFile import ImageFile
    
#Product imports
import NyThesaurus
from constants import *


def initialize(context):
    """ Naaya Thesaurus """

    context.registerClass(
        NyThesaurus.NyThesaurus,
        permission =   PERMISSION_ADD_NAAYATHESAURUS,
        constructors = (NyThesaurus.manage_addThesaurus_html,
                        NyThesaurus.manage_addThesaurus),
        icon='www/thesaurus.gif',
        )

misc_ = {
    #objects pics
    'thesaurus.gif':            ImageFile('www/thesaurus.gif', globals()),
    'thesaurus_catalog.gif':    ImageFile('www/thesaurus_catalog.gif', globals()),
    'themes.gif':               ImageFile('www/themes.gif', globals()),
    'concept_relations.gif':    ImageFile('www/concept_relations.gif', globals()),
    'concepts.gif':             ImageFile('www/concepts.gif', globals()),
    'terms.gif':                ImageFile('www/terms.gif', globals()),
    'alt_terms.gif':            ImageFile('www/alt_terms.gif', globals()),
    'scope_notes.gif':          ImageFile('www/scope_notes.gif', globals()),
    'definitions.gif':          ImageFile('www/definitions.gif', globals()),
    'theme_relations.gif':      ImageFile('www/theme_relations.gif', globals()),
    'source.gif':               ImageFile('www/source.gif', globals()),

    #layout pics
    'minus.gif':                ImageFile('www/minus.gif', globals()),
    'plus.gif':                 ImageFile('www/plus.gif', globals())
}
