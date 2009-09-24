# Python imports

# Zope imports
import Globals
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile

# Product imports
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils



manage_addGroupwareSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addGroupwareSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = 'gw' + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % ('gw', ut.utGenerateUID())
    self._setObject(id, GroupwareSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class GroupwareSite(NySite):
    """ """

    meta_type = 'Groupware site'
    #icon = 'misc_/GroupwareSite/site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)
        try:
            from Products.NaayaCore.SchemaTool.SchemaTool import manage_addSchemaTool
            manage_addSchemaTool(self)
        except ImportError:
            # this version of Naaya doesn't use Schemas; we can safely move on
            pass

        self.loadSkeleton(Globals.package_home(globals()))

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')
        self.manage_delObjects('info')

    gw_common_css = ImageFile('www/gw_common.css', globals())
    gw_print_css = ImageFile('www/gw_print.css', globals())
    gw_style_css = ImageFile('www/gw_style.css', globals())

InitializeClass(GroupwareSite)
