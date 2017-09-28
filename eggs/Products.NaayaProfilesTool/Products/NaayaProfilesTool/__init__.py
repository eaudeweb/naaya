from App.ImageFile import ImageFile
from Products.NaayaCore.constants import PERMISSION_ADD_NAAYACORE_TOOL

import ProfilesTool

import Products.NaayaCore
Products.NaayaCore.misc_.update({
    'Profile.gif':ImageFile('www/Profile.gif', globals()),
    'ProfileSheet.gif':ImageFile('www/ProfileSheet.gif', globals()),
    'ProfilesTool.gif':ImageFile('www/ProfilesTool.gif', globals())
})

def initialize(context):
    """ """
    context.registerClass(
        ProfilesTool.ProfilesTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                ProfilesTool.manage_addProfilesTool,
                ),
        icon = 'www/ProfilesTool.gif'
    )
