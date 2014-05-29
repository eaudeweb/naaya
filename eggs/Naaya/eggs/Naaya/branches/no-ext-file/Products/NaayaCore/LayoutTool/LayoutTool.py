"""This tool is used to customize the main templates, styles and layouts of a
Naaya Site

"""

import os.path

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import view_management_screens, view
import Products
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *
from managers.combosync_tool import combosync_tool
import Skin
from Style import Style
from naaya.core.zope2util import folder_manage_main_plus

def manage_addLayoutTool(self, REQUEST=None):
    """ """
    ob = LayoutTool(ID_LAYOUTTOOL, TITLE_LAYOUTTOOL)
    self._setObject(ID_LAYOUTTOOL, ob)
    ob_aq = self._getOb(ID_LAYOUTTOOL)
    ob_aq.loadDefaultData()
    view_perm = Permission(view, (), ob_aq)
    view_perm.setRoles(['Anonymous',])
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class LayoutTool(Folder, combosync_tool):
    """ """

    meta_type = METATYPE_LAYOUTTOOL
    icon = 'misc_/NaayaCore/LayoutTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Layout', 'action': 'manage_layout_html'},
        )
        +
        Folder.manage_options[3:]
    )

    meta_types = (
        {'name': METATYPE_SKIN, 'action': 'manage_addSkinForm', 'permission': PERMISSION_ADD_NAAYACORE_TOOL },
    )

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image', 'File']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        y.extend(self.meta_types)
        return y

    manage_addSkinForm = Skin.manage_addSkinForm
    manage_addSkin = Skin.manage_addSkin

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.__current_skin_id = None
        self.__current_skin_scheme_id = None
        combosync_tool.__dict__['__init__'](self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        pass

    def getSkinsList(self): return self.objectValues(METATYPE_SKIN)
    def getCurrentSkinId(self): return self.__current_skin_id
    def getCurrentSkinSchemeId(self): return self.__current_skin_scheme_id
    def getCurrentSkin(self): return self._getOb(self.__current_skin_id)
    def getCurrentSkinScheme(self): return self._getOb(self.__current_skin_id)._getOb(self.__current_skin_scheme_id)
    def getCurrentSkinSchemes(self):
        try: return self._getOb(self.getCurrentSkinId()).getSchemes()
        except: return []

    def getSkinFilesPath(self):
        return '%s/%s' % (self._getOb(self.__current_skin_id).absolute_url(), self.getCurrentSkinSchemeId())

    def getDataForLayoutSettings(self):
        l_data = []
        for l_skin in self.getSkinsList():
            l_schemes = []
            for l_scheme in l_skin.getSchemes():
                l_schemes.append((l_scheme.title_or_id(), l_scheme.id))
            l_data.append((l_skin.id, l_skin.title_or_id(), l_schemes))
        return (self.__current_skin_id, self.getCurrentSkinSchemeId(), l_data)


    def get_current_skin(self):
        return self._getOb(self.__current_skin_id)

    def get_skin_files_path(self):
        return '%s/%s' % (self.get_current_skin().absolute_url(), self.getCurrentSkinSchemeId())

    def getContent(self, p_context={}, p_page=None):
        p_context['skin_files_path'] = self.get_skin_files_path()
        return self.get_current_skin()._getOb(p_page).pt_render(extra_context=p_context)

    def getNaayaContentStyles(self):
        ny_content = self.get_pluggable_content()
        res = []
        for v in ny_content.values():
            if v.has_key('additional_style') and v['additional_style']:
                style = v['additional_style']
                if callable(style):
                    style = style()
                res.append('/* Begin %s styles*/' % v['meta_type'])
                res.append(style)
                res.append('/* End %s styles*/\n' % v['meta_type'])
        return '\n'.join(res)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageLayout')
    def manageLayout(self, theMasterList='', theSlaveList='', REQUEST=None):
        """ """
        self.__current_skin_id = theMasterList
        self.__current_skin_scheme_id = theSlaveList
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_layout_html')

    _standard_template = PageTemplateFile('zpt/standard_template', globals())
    def get_standard_template(self):
        try:
            return self.get_current_skin().aq_self.standard_template
        except AttributeError:
            return self.get_standard_template_base()

    _blank_page = PageTemplateFile('zpt/blank_page.zpt', globals())
    def render_standard_template(self, context):
        return self._blank_page.aq_base.__of__(context)()

    def get_standard_template_base(self):
        return self._standard_template

    def getCurrentStyleObjects(self):
        """
        Returns all the style objects in the current skin and current scheme
        """
        skin = self.getCurrentSkin()
        scheme = self.getCurrentSkinScheme()

        ret = []
        for item in skin.objectValues():
            if isinstance(item, Style):
                ret.append(item)

        for item in scheme.objectValues():
            if isinstance(item, Style):
                ret.append(item)

        return ret

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_layout_html')
    manage_layout_html = PageTemplateFile('zpt/layout_layout', globals())

    manage_main = folder_manage_main_plus
    ny_before_listing = PageTemplateFile('zpt/manage_main_header', globals())

InitializeClass(LayoutTool)


class AdditionalStyle(object):

    def __init__(self, css_path, globals_=None):
        if globals_ is not None:
            dirname = os.path.dirname(globals_['__file__'])
            css_path = os.path.join(dirname, css_path)
        self.css_path = css_path
        self.last_mtime = None

    def _patch_content(self, value):
        out = ["/* %s */" % self.css_path]
        for i, line in enumerate(value.splitlines()):
            out.append("/*%3d*/ %s" % (i+1, line))
        return "\n".join(out)

    def __call__(self):
        mtime = os.stat(self.css_path).st_mtime
        if mtime > self.last_mtime:
            f = open(self.css_path, 'rb')
            self.content = self._patch_content(f.read())
            f.close()
            self.last_mtime = mtime
        return self.content
