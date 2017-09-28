import os
from App.ImageFile import ImageFile

def initialize(context):
    """ """
    from constants import PERMISSION_ADD_SITE, PERMISSION_ADD_FOLDER
    from naaya.content.base import discover
    import NySite
    import NyFolder
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
        icon = 'www/NyFolder.png'
        )

    #initialize NaayaContent
    discover.initialize(context)

    from Products.NaayaCore.LayoutTool.DiskFile import allow_path
    allow_path('Products.Naaya:skel/layout/')

misc_ = {
    'NyFolder.png':ImageFile('www/NyFolder.png', globals()),
    'NyFolder_marked.gif':ImageFile('www/NyFolder_marked.gif', globals()),
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'addcomment.gif': ImageFile('www/addcomment.gif', globals()),
    'ajax-loader.gif': ImageFile('www/ajax-loader.gif', globals()),
    'checked':ImageFile('www/checked.png', globals()),
    'checkin':ImageFile('www/checkin.gif', globals()),
    'checkout':ImageFile('www/checkout.gif', globals()),
    'close.png': ImageFile('www/close.png', globals()),
    'comment.gif': ImageFile('www/comment.gif', globals()),
    'conflict_users.png': ImageFile('www/conflict_users.png', globals()),
    'copy.gif':ImageFile('www/copy.gif', globals()),
    'cut.gif':ImageFile('www/cut.gif', globals()),
    'delete.gif':ImageFile('www/delete.gif', globals()),
    'download-file.png':ImageFile('www/download-file.png', globals()),
    'download.png': ImageFile('www/download.png', globals()),
    'edit':ImageFile('www/edit.gif', globals()),
    'facebook.png':ImageFile('www/facebook.png', globals()),
    'fullscreencollapse_icon.gif':ImageFile('www/fullscreencollapse_icon.gif', globals()),
    'fullscreenexpand_icon.gif':ImageFile('www/fullscreenexpand_icon.gif', globals()),
    'gadfly_container.gif': ImageFile('www/gadfly_container.gif', globals()),
    'indicator.gif': ImageFile('www/indicator.gif', globals()),
    'info.png': ImageFile('www/info.png', globals()),
    'linkedin.png': ImageFile('www/linkedin.png', globals()),
    'logintoadd.gif': ImageFile('www/logintoadd.gif', globals()),
    'minus.gif':ImageFile('www/minus.gif', globals()),
    'paste.gif':ImageFile('www/paste.gif', globals()),
    'plus.gif':ImageFile('www/plus.gif', globals()),
    'powered.gif':ImageFile('www/powered.gif', globals()),
    'printer.gif': ImageFile('www/printer.gif', globals()),
    'revoke_permission.png': ImageFile('www/revoke_permission.png', globals()),
    'rss.png': ImageFile('www/rss.png', globals()),
    'select_all.gif':ImageFile('www/select_all.gif', globals()),
    'sort_asc.gif':ImageFile('www/sort_asc.gif', globals()),
    'sort_desc.gif':ImageFile('www/sort_desc.gif', globals()),
    'sort_not.gif':ImageFile('www/sort_not.gif', globals()),
    'spacer.gif':ImageFile('www/spacer.gif', globals()),
    'square.gif':ImageFile('www/square.gif', globals()),
    'star.png':ImageFile('www/star.png', globals()),
    'trash.gif': ImageFile('www/trash.gif', globals()),
    'twitter.png': ImageFile('www/twitter.png', globals()),

    #drag & drop files
    'core.js': ImageFile('zpt/dragdrop/core.js.dtml', globals()),
    'events.js': ImageFile('zpt/dragdrop/events.js.dtml', globals()),
    'css.js': ImageFile('zpt/dragdrop/css.js.dtml', globals()),
    'coordinates.js': ImageFile('zpt/dragdrop/coordinates.js.dtml', globals()),
    'drag.js': ImageFile('zpt/dragdrop/drag.js.dtml', globals()),
    'dragsort.js': ImageFile('zpt/dragdrop/dragsort.js.dtml', globals()),
    'cookies.js': ImageFile('zpt/dragdrop/cookies.js.dtml', globals()),

    # documentation
    'admin_schema':ImageFile('www/documentation/admin_schema.png', globals()),
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

    # Utilities JS
    'utils.js':ImageFile('www/js/utils.js', globals()),
    'mainsections.js':ImageFile('www/js/mainsections.js', globals()),
    'admin.js':ImageFile('www/js/admin.js', globals()),
    'json2.min.js':ImageFile('www/js/json2.min.js', globals()),

    # jQuery
    # Use jquery.js if version is of no importance
    'jquery.js':ImageFile('www/js/jquery-1.7.1.min.js', globals()),
    'jquery.min.js':ImageFile('www/js/jquery-1.7.1.min.js', globals()),

    # jQuery plugins
    'jquery-ui.js':ImageFile('www/js/jquery-ui-1.9.2.min.js', globals()),
    'jquery.cookie.js':ImageFile('www/js/jquery.cookie.js', globals()),
    'jquery.bgiframe.min.js':ImageFile('www/js/jquery.bgiframe.min.js', globals()),
    'jquery.autocomplete.min.js':ImageFile('www/js/jquery.autocomplete.min.js', globals()),
    'jquery.tree.init.js':ImageFile('www/js/jquery.tree.init.js', globals()),
    'jquery.form.js':ImageFile('www/js/jquery.form.js', globals()),
    'jquery.tooltip.min.js':ImageFile('www/js/jquery.tooltip.min.js', globals()),

    #CSS files
    'jquery-ui.css':ImageFile('www/js/css/jquery-ui.css', globals()),
    'jquery.autocomplete.css':ImageFile('www/js/css/jquery.autocomplete.css', globals()),
    'jquery.tooltip.css':ImageFile('www/js/css/jquery.tooltip.css', globals()),

    #Event index
    'yes.gif':ImageFile('www/yes.gif', globals()),
    'no.gif':ImageFile('www/no.gif', globals()),
}

def register_content(module, klass, module_methods, klass_methods, add_method):
    """ To be called from content type you want to register within Naaya Folder.

    module_methods = {METHOD_1: PERMISSION_1, METHOD_2: PERMISSION_2}
    klass_methods  = {METHOD_1: PERMISSION_1, METHOD_2: PERMISSION_2}
    add_method = ('METHOD_ADD_HTML', 'PERMISSION')

    See NaayaForum for an example.
    """
    import zLOG
    from AccessControl import ClassSecurityInfo
    from Globals import InitializeClass
    import NyFolder
    import NyFolderBase

    security = ClassSecurityInfo()
    NyFolderBase.NyFolderBase.security = security

    # Register module methods
    for meth, permission in module_methods.items():
        meth_obj = getattr(module, meth, None)
        if not meth_obj:
            continue
        setattr(NyFolderBase.NyFolderBase, meth, meth_obj)
        if permission:
            NyFolderBase.NyFolderBase.security.declareProtected(permission, meth)

    # Register class methods
    for meth, permission in klass_methods.items():
        meth_obj = getattr(klass, meth, None)
        if not meth_obj:
            continue
        setattr(NyFolderBase.NyFolderBase, meth, meth_obj)
        if permission:
            NyFolderBase.NyFolderBase.security.declareProtected(permission, meth)

    klass_label = getattr(klass, 'meta_label', klass.meta_type)
    add_meth, add_perm = add_method
    NyFolderBase.NyFolderBase._dynamic_content_types[klass.meta_type] = (add_meth, klass_label, add_perm)
    zLOG.LOG(module.__name__, zLOG.INFO,
             'Dynamic module "%s" registered' % klass.__name__)

    InitializeClass(NyFolder.NyFolder)


def naaya_bundle_registration():
    """ Register things from skel into the Naaya bundle """
    from Products.NaayaCore.FormsTool import bundlesupport
    templates_path = os.path.join(os.path.dirname(__file__), 'skel', 'forms')
    bundlesupport.register_templates_in_directory(templates_path, 'Naaya')
