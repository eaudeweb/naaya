from os.path import join

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.utils import (get_portals, get_portal,
                                         get_portal_path, readFile)

class UpdateLayout(UpdateScript):
    """ Update Portal layout script  """
    title = 'Update portal layout'
    authors = ['Alec Ghica']
    creation_date = 'Jan 01, 2010'
    security = ClassSecurityInfo()

    def __init__(self):
        """ constructor """
        self.pskins = {'skin':'Naaya skin', 'smap':'SMAP skin', 'chm':'CHM skin', 'semide':'SEMIDE skin', \
                       'envirowindows':'EnviroWindows skin'}

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/update_layout', globals())

    security.declareProtected(view_management_screens, 'updateLayout')
    def updateLayout(self, ppath='', all=False, portals='', p_action='ep',
                     sel_skin='', locator='skin', f_action='af', file_id='', REQUEST=None):
        """ update files for Naaya layout """
        report = {}
        portals_custom = []
        for portal_id in portals.split(','):
            portals_custom.append(portal_id.strip())

        if all:
            portals_list = get_portals(self, self.pmeta_types)
            for portal in portals_list:
                do_update = False
                if p_action == 'ep':
                    if not portal.id in portals_custom: do_update = True
                else:
                    if portal.id in portals_custom: do_update = True
                if do_update:
                    report[portal.id] = self.updateLayoutForms(portal, locator, sel_skin, f_action, file_id)
        else:
            portal = get_portal(self, ppath)
            if not portal.id in portals_custom:
                report[portal.id] = self.updateLayoutForms(portal, locator, sel_skin, f_action, file_id)

        REQUEST.SESSION.set('report', report)
        return REQUEST.RESPONSE.redirect('%s/update_layout_html' % self.absolute_url())

    security.declareProtected(view_management_screens, 'updateLayoutForms')
    def updateLayoutForms(self, portal, locator, skin_id, f_action, file_id):
        """ reload Naaya portal layout files"""
        report = {}
        portal_path = portal.absolute_url(1)
        file_custom = []
        for fid in file_id.split(','):
            file_custom.append(fid.strip())

        if f_action == 'if':
            for file_id in file_custom:
                if locator == 'skin':
                    form_path = '%s/portal_layout/%s/%s' % (portal_path, skin_id, file_id)
                    form_fs = self.get_fs_layout_content(portal, skin_id, '', file_id)
                    form_zmi = self.get_zmi_template(form_path)
                    report['../portal_layout/%s/%s' % (skin_id, file_id)] = 'updated'
                    self.update_layout_file(portal, file_id, form_fs, form_zmi, skin_id, '', 'template')
                else:
                    for scheme_id in self.list_fs_skinfiles(portal, skin_id, True):
                        rtype = 'r'
                        file_type = 'style'
                        form_path = '%s/portal_layout/%s/%s/%s' % (portal_path, skin_id, scheme_id, file_id)
                        file_type = self.get_scheme_filetype(file_id)
                        if file_type == 'image': rtype = 'rb'
                        form_fs = self.get_fs_layout_content(portal, skin_id, scheme_id, file_id, rtype)
                        form_zmi = self.get_zmi_template(form_path)
                        report['../portal_layout/%s/%s/%s' % (skin_id, scheme_id, file_id)] = 'updated'
                        self.update_layout_file(portal, file_id, form_fs, form_zmi, skin_id, scheme_id, file_type)
        else:
            if locator == 'skin':
                for file_id in self.list_fs_skinfiles(portal, skin_id, False):
                    do_update = True
                    if f_action == 'ef':
                        if file_id in file_custom: do_update = False
                    if do_update:
                        form_path = '%s/portal_layout/%s/%s' % (portal_path, skin_id, file_id)
                        form_fs = self.get_fs_layout_content(portal, skin_id, '', file_id)
                        form_zmi = self.get_zmi_template(form_path)
                        report['../portal_layout/%s/%s' % (skin_id, file_id)] = 'updated'
                        self.update_layout_file(portal, file_id, form_fs, form_zmi, skin_id, '', 'template')
            else:
                for scheme_id in self.list_fs_skinfiles(portal, skin_id, True):
                    for file_id in self.list_fs_schemefiles(portal, skin_id, scheme_id, ftype='styles'):
                        do_update = True
                        if f_action == 'ef':
                            if file_id in file_custom: do_update = False
                        if do_update:
                            form_path = '%s/portal_layout/%s/%s/%s' % (portal_path, skin_id, scheme_id, file_id)
                            form_fs = self.get_fs_layout_content(portal, skin_id, scheme_id, file_id)
                            form_zmi = self.get_zmi_template(form_path)
                            report['../portal_layout/%s/%s/%s' % (skin_id, scheme_id, file_id)] = 'updated'
                            self.update_layout_file(portal, file_id, form_fs, form_zmi, skin_id, scheme_id, 'style')
                    for file_id in self.list_fs_schemefiles(portal, skin_id, scheme_id, ftype='images'):
                        do_update = True
                        if f_action == 'ef':
                            if file_id in file_custom: do_update = False
                        if do_update:
                            form_path = '%s/portal_layout/%s/%s/%s' % (portal_path, skin_id, scheme_id, file_id)
                            form_fs = self.get_fs_layout_content(portal, skin_id, scheme_id, file_id, 'rb')
                            form_zmi = self.get_zmi_template(form_path)
                            report['../portal_layout/%s/%s/%s' % (skin_id, scheme_id, file_id)] = 'updated'
                            self.update_layout_file(portal, file_id, form_fs, form_zmi, skin_id, scheme_id, 'image')
        return report

    security.declarePrivate('update_layout_file')
    def update_layout_file(self, portal, file_id, form_fs, form_zmi, skin_id, scheme_id, location='template'):
        """ """
        if form_fs and form_zmi:
            if not create_signature(form_fs) == create_signature(self.get_template_content(form_zmi)):
                try:
                    if location == 'image':
                        form_zmi.update_data(data=form_fs)
                        form_zmi._p_changed = 1
                    else:
                        form_zmi.pt_edit(text=form_fs, content_type='')
                        form_zmi._p_changed = 1
                except Exception, error:
                    print error
        if form_fs and not form_zmi:
            try:
                layouttool_ob = portal.getLayoutTool()
                skin_ob = layouttool_ob._getOb(skin_id)
                if location == 'template':
                    skin_ob.manage_addTemplate(id=file_id, title='', file='')
                    template_ob = skin_ob._getOb(file_id, None)
                    template_ob.pt_edit(text=form_fs, content_type='')
                    template_ob._p_changed = 1
                elif location == 'style':
                    scheme_ob = skin_ob._getOb(scheme_id)
                    scheme_ob.manage_addStyle(id=file_id, title='', file='')
                    style_ob = scheme_ob._getOb(file_id, None)
                    style_ob.pt_edit(text=form_fs, content_type='')
                    style_ob._p_changed = 1
                else:
                    scheme_ob = skin_ob._getOb(scheme_id)
                    scheme_ob.manage_addImage(id=file_id, file='', title='')
                    image_ob = scheme_ob._getOb(file_id)
                    image_ob.update_data(data=form_fs)
                    image_ob._p_changed=1
            except Exception, error:
                print error

    security.declarePrivate('list_fs_skinfiles')
    def list_fs_skinfiles(self, portal, skin_id, schemes=False):
        """
            return the list of the filesystem templates
        """
        portal_path = get_portal_path(self, portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.layout is not None:
            for skin in skel_handler.root.layout.skins:
                if skin.id == skin_id:
                    if schemes:
                        return [s.id for s in skin.schemes]
                    else:
                        return [f.id for f in skin.templates]
        return []

    security.declarePrivate('list_fs_schemefiles')
    def list_fs_schemefiles(self, portal, skin_id, scheme_id, ftype='styles'):
        """
            return the list of the filesystem templates
        """
        portal_path = get_portal_path(self, portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.layout is not None:
            for skin in skel_handler.root.layout.skins:
                if skin.id == skin_id:
                    for scheme in skin.schemes:
                        if scheme.id == scheme_id:
                            if ftype == 'styles':
                                return [s.id for s in scheme.styles]
                            else:
                                return [i.id for i in scheme.images]

    security.declarePrivate('get_fs_layout_content')
    def get_fs_layout_content(self, portal, skin_id, scheme_id, file_id, rtype='r'):
        """
            return the content of the filesystem layout file
        """
        portal_path = get_portal_path(self, portal)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.layout is not None:
            if scheme_id:
                file_ext = ''
                if rtype == 'r': file_ext = '.css'
                return readFile(join(portal_path, 'skel', 'layout', skin_id, scheme_id, '%s%s' % (file_id, file_ext)), rtype)
            else:
                return readFile(join(portal_path, 'skel', 'layout', skin_id, '%s.zpt' % file_id), 'r')

    security.declarePrivate('get_scheme_filetype')
    def get_scheme_filetype(self, file_id):
        """ """
        if file_id in ['style', 'style_rtl', 'style_common', 'style_common_rtl', 'style_handheld', 'style_handheld_rtl', 'style_print', 'common', 'print']:
            return 'style'
        return 'image'
