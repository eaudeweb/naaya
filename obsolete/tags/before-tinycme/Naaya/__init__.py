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

#Python imports

#Zope imports
from ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

#Product imports
from constants import *
from Products.NaayaContent import get_pluggable_content
import NySite
import NyFolder

def initialize(context):
    """ """

    #register classes
    context.registerClass(
        NySite.NySite,
        permission = PERMISSION_ADD_SITE,
        constructors = (
                NySite.manage_addNySite_html,
                NySite.manage_addNySite,
                ),
        icon = 'www/Site.gif'
        )
    context.registerClass(
        NyFolder.NyFolder,
        permission = PERMISSION_ADD_FOLDER,
        constructors = (
                NyFolder.manage_addNyFolder_html,
                NyFolder.folder_add_html,
                NyFolder.addNyFolder,
                ),
        icon = 'www/NyFolder.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'NyFolder.gif':ImageFile('www/NyFolder.gif', globals()),
    'NyFolder_marked.gif':ImageFile('www/NyFolder_marked.gif', globals()),

    'spacer.gif':ImageFile('www/spacer.gif', globals()),
    'square.gif':ImageFile('www/square.gif', globals()),
    'plus.gif':ImageFile('www/plus.gif', globals()),
    'minus.gif':ImageFile('www/minus.gif', globals()),
    'sort_asc.gif':ImageFile('www/sort_asc.gif', globals()),
    'sort_desc.gif':ImageFile('www/sort_desc.gif', globals()),
    'sort_not.gif':ImageFile('www/sort_not.gif', globals()),

    'select_all.gif':ImageFile('www/select_all.gif', globals()),
    'copy.gif':ImageFile('www/copy.gif', globals()),
    'cut.gif':ImageFile('www/cut.gif', globals()),
    'delete.gif':ImageFile('www/delete.gif', globals()),
    'paste.gif':ImageFile('www/paste.gif', globals()),
    'edit':ImageFile('www/edit.gif', globals()),
    'checkin':ImageFile('www/checkin.gif', globals()),
    'checkout':ImageFile('www/checkout.gif', globals()),
    'checked':ImageFile('www/checked.png', globals()),
    'star.png':ImageFile('www/star.png', globals()),
    'fullscreencollapse_icon.gif':ImageFile('www/fullscreencollapse_icon.gif', globals()),
    'fullscreenexpand_icon.gif':ImageFile('www/fullscreenexpand_icon.gif', globals()),
    'gadfly_container.gif': ImageFile('www/gadfly_container.gif', globals()),

    #drag & drop files
    'core.js': ImageFile('zpt/dragdrop/core.js.dtml', globals()),
    'events.js': ImageFile('zpt/dragdrop/events.js.dtml', globals()),
    'css.js': ImageFile('zpt/dragdrop/css.js.dtml', globals()),
    'coordinates.js': ImageFile('zpt/dragdrop/coordinates.js.dtml', globals()),
    'drag.js': ImageFile('zpt/dragdrop/drag.js.dtml', globals()),
    'dragsort.js': ImageFile('zpt/dragdrop/dragsort.js.dtml', globals()),
    'cookies.js': ImageFile('zpt/dragdrop/cookies.js.dtml', globals()),

    # documentation
    'admin_schema':ImageFile('www/documentation/admin_schema.gif', globals()),
    'workflow':ImageFile('www/documentation/workflow.gif', globals()),
    'brief_layout':ImageFile('www/documentation/brief_layout.gif', globals()),
    'select_language_box':ImageFile('www/documentation/select_language_box.gif', globals()),
    'translate_edit':ImageFile('www/documentation/translate_edit.gif', globals()),
    'translate_add':ImageFile('www/documentation/translate_add.gif', globals()),
    'translate_tooltips':ImageFile('www/documentation/translate_tooltips.gif', globals()),
    'translate_demo':ImageFile('www/documentation/translate_demo.gif', globals()),
    'translate_messages':ImageFile('www/documentation/translate_messages.gif', globals()),

    #calendar
    'icon_calendar.gif':ImageFile('www/icon_calendar.gif', globals()),
    'nav-bg.gif':ImageFile('www/nav-bg.gif', globals()),
    'default-bg.gif':ImageFile('www/default-bg.gif', globals()),
}

#constructors for pluggable content
security = ClassSecurityInfo()
NyFolder.NyFolder.security = security
for k,v in get_pluggable_content().items():
    for cns in v['constructors']:
        c = 'from Products.NaayaContent.%s import %s' % (v['module'], v['module'])
        exec(c)
        c = 'NyFolder.NyFolder.%s = %s.%s' % (cns, v['module'], cns)
        exec(c)
        NyFolder.NyFolder.security.declareProtected(v['permission'], cns)
InitializeClass(NyFolder.NyFolder)

#make drag & drop available globally
def DragDropCore(self, name):
    """ """
    js_data = []
    js_data.append('<script src="misc_/Naaya/core.js" type="text/javascript"></script>')
    js_data.append('<script src="misc_/Naaya/events.js" type="text/javascript"></script>')
    js_data.append('<script src="misc_/Naaya/css.js" type="text/javascript"></script>')
    js_data.append('<script src="misc_/Naaya/coordinates.js" type="text/javascript"></script>')
    js_data.append('<script src="misc_/Naaya/drag.js" type="text/javascript"></script>')
    js_data.append('<script src="misc_/Naaya/dragsort.js" type="text/javascript"></script>')
    js_data.append('<script src="misc_/Naaya/cookies.js" type="text/javascript"></script>')
    js_data.append('<script type="text/javascript">')
    js_data.append('<!--')
    js_data.append('''var dragsort = ToolMan.dragsort()
        var junkdrawer = ToolMan.junkdrawer()

        ddl_oldonload = window.onload
        window.onload = function() {
            dragsort.makeListSortable(document.getElementById("%s"), verticalOnly, saveOrder)
            if(ddl_oldonload)
                ddl_oldonload()
        }

        function verticalOnly(item) {
            item.toolManDragGroup.verticalOnly()
        }

        function speak(id, what) {
            var element = document.getElementById(id);
            element.innerHTML = 'Clicked ' + what;
        }

        function saveOrder(item) {
            var group = item.toolManDragGroup
            var list = group.element.parentNode
            var id = list.getAttribute("id")
            if (id == null) return
            group.register('dragend', function() {
                ToolMan.cookies().set("list-" + id, 
                        junkdrawer.serializeList(list), 365)
            })
        }''' % name)
    js_data.append('//-->')
    js_data.append('</script>')
    return '\n'.join(js_data)

def DragDropHidden(self, p_items):
    """ """
    return '<input type="hidden" name="positions" value="%s" />' % '|'.join([x.id for x in p_items])

methods = {
    'DragDropCore': DragDropCore,
    'DragDropHidden': DragDropHidden,
}
