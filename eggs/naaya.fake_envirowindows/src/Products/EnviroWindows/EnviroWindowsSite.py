from Globals import InitializeClass
from App.ImageFile import ImageFile
#from Products.Naaya.NySite import NySite
from naaya.groupware.groupware_site import GroupwareSite

class EnviroWindowsSite(GroupwareSite):	# NySite):
    """ """
    meta_type = "Groupware site"

    ew_common_css = ImageFile('www/ew_common.css', globals())
    ew_print_css = ImageFile('www/ew_print.css', globals())
    ew_style_css = ImageFile('www/ew_style.css', globals())

    manage_options = (
        GroupwareSite.manage_options
    )

InitializeClass(EnviroWindowsSite)
