from Globals import InitializeClass
from App.ImageFile import ImageFile
from Products.Naaya.NySite import NySite

class EnviroWindowsSite(NySite):
    """ """
    meta_type = "Groupware site"

    ew_common_css = ImageFile('www/ew_common.css', globals())
    ew_print_css = ImageFile('www/ew_print.css', globals())
    ew_style_css = ImageFile('www/ew_style.css', globals())

    manage_options = (
        NySite.manage_options
    )

InitializeClass(EnviroWindowsSite)
