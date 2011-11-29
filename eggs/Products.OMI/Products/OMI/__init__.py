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
# Alex Morega, Eau de Web
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from App.ImageFile import ImageFile
from StaticServe import StaticServeFromZip

import FactsheetFolder
import Factsheet
import FactsheetComment
from constants import *

try:
    from Products.Naaya import register_content
    from Products.Naaya.NyFolderBase import NyFolderBase
except ImportError:
    pass
else:
    register_content(
        module=FactsheetFolder,
        klass=FactsheetFolder.FactsheetFolder,
        module_methods={'manage_addFactsheetFolder_html': ADD_FACTSHEET_FOLDER},
        klass_methods={},
        add_method=('manage_addFactsheetFolder_html', ADD_FACTSHEET_FOLDER),
    )
    NyFolderBase.manage_addFactsheetFolder = FactsheetFolder.manage_addFactsheetFolder

def initialize(context):
    context.registerClass(
                          FactsheetComment.FactsheetComment,
                          permission=ADD_FACTSHEET_COMMENT,
                          constructors=(FactsheetComment.manage_addComment_html,
                          FactsheetComment.manage_addComment),
                          )
    context.registerClass(
                          Factsheet.Factsheet,
                          permission=ADD_FACTSHEET,
                          constructors=(Factsheet.manage_addFactsheet_html,),
                          icon='www/Factsheet.gif',
                          )
    context.registerClass(
                          FactsheetFolder.FactsheetFolder,
                          permission=ADD_FACTSHEET_FOLDER,
                          constructors=(FactsheetFolder.manage_addFactsheetFolder_html,
                                        FactsheetFolder.manage_addFactsheetFolder),
                          icon='www/FactsheetFolder.gif',
                          )

misc_ = {
    'style.css': ImageFile('www/ew.style.css', globals()),
    'localstyle.css': ImageFile('www/style.css', globals()),
    'factsheet.js': ImageFile('www/factsheet.js', globals()),
    'AjaxRequest.js': ImageFile('www/AjaxRequest.js', globals()),
    'tinymce': StaticServeFromZip('', 'www/tinymce_3_2_4_1.zip', globals()),
}
