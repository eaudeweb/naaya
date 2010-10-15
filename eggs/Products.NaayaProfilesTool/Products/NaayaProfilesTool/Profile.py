""" User profile is a layer above normal users. It is used to provide support
for custom fields for users such as addresses and phone numbers

"""
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from constants import METATYPE_PROFILE, METATYPE_PROFILESHEET
from Products.NaayaCore.managers.utils import utils

def manage_addProfile(self, id, title='', REQUEST=None):
    """ """
    ob = Profile(id, title)
    self._setObject(id, ob)
    self.loadProfileSheets(self._getOb(id))
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Profile(Folder, utils):
    """
    Class that implements the user profile.
    """

    meta_type = METATYPE_PROFILE
    icon = 'misc_/NaayaCore/Profile.gif'

    manage_options = (
        Folder.manage_options
    )

    meta_types = ()
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    def getSheets(self):
        """
        Returns a list with all profile sheets.
        """
        return self.objectValues(METATYPE_PROFILESHEET)

    def getSheetById(self, id):
        """ """
        return self._getOb(id, None)

InitializeClass(Profile)
