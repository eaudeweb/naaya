from AccessControl import ClassSecurityInfo
from App.ImageFile import ImageFile
from Globals import InitializeClass
from naaya.groupware.groupware_site import GroupwareSite
from Products.NaayaCore.managers.utils import utils


class EnviroWindowsSite(GroupwareSite):	# NySite):
    """ """
    meta_type = "Groupware site"
    security = ClassSecurityInfo()

    ew_common_css = ImageFile('www/ew_common.css', globals())
    ew_print_css = ImageFile('www/ew_print.css', globals())
    ew_style_css = ImageFile('www/ew_style.css', globals())

    manage_options = (
        GroupwareSite.manage_options
    )

    security.declarePublic('stripAllHtmlTags')
    def stripAllHtmlTags(self, p_text):
        """ """
        return utils().utStripAllHtmlTags(p_text)

InitializeClass(EnviroWindowsSite)
