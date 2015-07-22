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
import zLOG
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

#Product imports
from constants import *
from Products.NaayaContent.discover import get_pluggable_content
from Products.NaayaContent import discover
import NySite
import NyFolder
from managers import initialize as managers_initialize

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


def initialize(context):
    """ """
    managers_initialize(context)
    
    #register classes
    context.registerClass(
        NySite.NySite,
        permission = PERMISSION_ADD_SITE,
        constructors = (
                NySite.manage_addNySite_html,
                NySite.manage_addNySite,
                ),
        icon = 'www/Site.gif',
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

    #initialize NaayaContent
    discover.initialize(context)

methods = {
    'DragDropCore': DragDropCore,
    'DragDropHidden': DragDropHidden,
}

misc_ = {
    'addcomment.gif': ImageFile('www/addcomment.gif', globals()),
    'checked':ImageFile('www/checked.png', globals()),
    'checkin':ImageFile('www/checkin.gif', globals()),
    'checkout':ImageFile('www/checkout.gif', globals()),
    'comment.gif': ImageFile('www/comment.gif', globals()),
    'copy.gif':ImageFile('www/copy.gif', globals()),
    'cut.gif':ImageFile('www/cut.gif', globals()),
    'delete.gif':ImageFile('www/delete.gif', globals()),
    'edit':ImageFile('www/edit.gif', globals()),
    'fullscreencollapse_icon.gif':ImageFile('www/fullscreencollapse_icon.gif', globals()),
    'fullscreenexpand_icon.gif':ImageFile('www/fullscreenexpand_icon.gif', globals()),
    'gadfly_container.gif': ImageFile('www/gadfly_container.gif', globals()),
    'minus.gif':ImageFile('www/minus.gif', globals()),
    'logintoadd.gif': ImageFile('www/logintoadd.gif', globals()),
    'NyFolder.gif':ImageFile('www/NyFolder.gif', globals()),
    'NyFolder_marked.gif':ImageFile('www/NyFolder_marked.gif', globals()),
    'paste.gif':ImageFile('www/paste.gif', globals()),
    'plus.gif':ImageFile('www/plus.gif', globals()),
    'powered.gif':ImageFile('www/powered.gif', globals()),
    'printer.gif': ImageFile('www/printer.gif', globals()),
    'select_all.gif':ImageFile('www/select_all.gif', globals()),
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'sort_asc.gif':ImageFile('www/sort_asc.gif', globals()),
    'sort_desc.gif':ImageFile('www/sort_desc.gif', globals()),
    'sort_not.gif':ImageFile('www/sort_not.gif', globals()),
    'spacer.gif':ImageFile('www/spacer.gif', globals()),
    'square.gif':ImageFile('www/square.gif', globals()),
    'star.png':ImageFile('www/star.png', globals()),
    'trash.gif': ImageFile('www/trash.gif', globals()),

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

    # jQuery
    'jquery-1.3.2.min.js':ImageFile('www/jquery-1.3.2.min.js', globals()),
    'jquery-ui-1.7.2.full.min.js':ImageFile('www/jquery-ui-1.7.2.full.min.js', globals()),
}

#register NaayaContent misc_
from OFS.Application import Application
from OFS.misc_ import Misc_
nyc_misc = Misc_('NaayaContent', discover.misc_)
Application.misc_.__dict__['NaayaContent'] = nyc_misc

def register_content(module, klass, module_methods, klass_methods, add_method):
    """ To be called from content type you want to register within Naaya Folder.
    
    module_methods = {METHOD_1: PERMISSION_1, METHOD_2: PERMISSION_2}
    klass_methods  = {METHOD_1: PERMISSION_1, METHOD_2: PERMISSION_2}
    add_method = ('METHOD_ADD_HTML', 'PERMISSION')
    
    See NaayaForum for an example.
    """
    security = ClassSecurityInfo()
    NyFolder.NyFolder.security = security
    
    # Register module methods
    for meth, permission in module_methods.items():
        meth_obj = getattr(module, meth, None)
        if not meth_obj:
            continue
        setattr(NyFolder.NyFolder, meth, meth_obj)
        if permission:
            NyFolder.NyFolder.security.declareProtected(permission, meth)
    
    # Register class methods
    for meth, permission in klass_methods.items():
        meth_obj = getattr(klass, meth, None)
        if not meth_obj:
            continue
        setattr(NyFolder.NyFolder, meth, meth_obj)
        if permission:
            NyFolder.NyFolder.security.declareProtected(permission, meth)
    
    klass_label = getattr(klass, 'meta_label', klass.meta_type)
    add_meth, add_perm = add_method
    NyFolder.NyFolder._dynamic_content_types[klass.meta_type] = (add_meth, klass_label, add_perm)
    zLOG.LOG(module.__name__, zLOG.INFO,
             'Dynamic module "%s" registered' % klass.__name__)

    InitializeClass(NyFolder.NyFolder)

#constructors for pluggable content
security = ClassSecurityInfo()
NyFolder.NyFolder.security = security
for k,v in get_pluggable_content().items():
    if k == 'Naaya Folder':
        continue
    for cns in v['constructors']:
        c = 'from Products.NaayaContent.%s import %s' % (v['module'], v['module'])
        exec(c)
        c = 'NyFolder.NyFolder.%s = %s.%s' % (cns, v['module'], cns)
        exec(c)
        NyFolder.NyFolder.security.declareProtected(v['permission'], cns)

InitializeClass(NyFolder.NyFolder)
