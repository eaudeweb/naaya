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
# Ghica Alexandru, Finsiel Romania

#Zope imports
from App.ImageFile import ImageFile

#Product imports
import NyGlossary
from constants import *


def initialize(context):
    """ Naaya Glossary """

    context.registerClass(
        NyGlossary.NyGlossary,
        permission =   PERMISSION_ADD_NAAYAGLOSSARY,
        constructors = (NyGlossary.manage_addGlossaryCentre_html,
                        NyGlossary.manage_addGlossaryCentre),
        icon='www/glossary.gif',
        )

misc_ = {
    'glossary.gif':         ImageFile('www/glossary.gif', globals()),
    'element.gif':          ImageFile('www/element.gif', globals()),
    'folder.gif':           ImageFile('www/folder.gif', globals()),
    'line.gif':             ImageFile('www/line.gif', globals()),
    'new.gif':              ImageFile('www/new.gif', globals()),

    #glossary style
    'ico_searchhelp.gif':   ImageFile('www/ico_searchhelp.gif', globals()),
    's_lefttop.gif':        ImageFile('www/s_lefttop.gif', globals()),
    's_lefttop.gif':        ImageFile('www/s_lefttop.gif', globals()),
    's_toplines.gif':       ImageFile('www/s_toplines.gif', globals()),
    's_righttop.gif':       ImageFile('www/s_righttop.gif', globals()),
    's_leftbottom.gif':     ImageFile('www/s_leftbottom.gif', globals()),
    's_bottomlines.gif':    ImageFile('www/s_bottomlines.gif', globals()),
    's_rightbottom.gif':    ImageFile('www/s_rightbottom.gif', globals()),
    's_bcktop.gif':         ImageFile('www/s_bcktop.gif', globals()),
    's_bckbottom.gif':      ImageFile('www/s_bckbottom.gif', globals()),
    'searchGloss_butt.gif': ImageFile('www/searchGloss_butt.gif', globals()),
    'category.gif':         ImageFile('www/category.gif', globals()),
    'dotted.gif':           ImageFile('www/dotted.gif', globals()),
    'note_ico.gif':         ImageFile('www/note_ico.gif', globals()),
    'separ.gif':            ImageFile('www/separ.gif', globals()),
    'search_ico.gif':       ImageFile('www/search_ico.gif', globals()),
    'definition_ico.gif':   ImageFile('www/definition_ico.gif', globals()),
    'related_ico.gif':      ImageFile('www/related_ico.gif', globals()),
    'plus.gif':             ImageFile('www/plus.gif', globals()),
    'minus.gif':            ImageFile('www/minus.gif', globals()),
    'square.gif':           ImageFile('www/square.gif', globals()),
    # Javascripts
    'tree.js':              ImageFile('www/tree.js', globals()),
}
